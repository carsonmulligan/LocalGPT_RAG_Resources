#!/usr/bin/env python3
"""
Generate Enhanced Catalog for Maximum Quality RAG Packages
Creates catalog.json from all enhanced package metadata.
"""

import json
import os
from pathlib import Path
from datetime import datetime

def generate_enhanced_catalog():
    """Generate enhanced catalog from all package directories."""
    
    rag_packages_dir = Path("rag_packages")
    packages = []
    total_size_bytes = 0
    
    print("🔄 Generating enhanced catalog from maximum quality packages...")
    
    # Scan all package directories
    for package_dir in rag_packages_dir.iterdir():
        if package_dir.is_dir():
            package_info_file = package_dir / "package_info.json"
            if package_info_file.exists():
                try:
                    with open(package_info_file, 'r') as f:
                        package_info = json.load(f)
                        packages.append(package_info)
                        
                        # Calculate total size
                        vdb_size = package_info.get("vector_database", {}).get("size_bytes", 0)
                        index_size = package_info.get("ios_index", {}).get("size_bytes", 0)
                        total_size_bytes += vdb_size + index_size
                        
                        print(f"   ✅ {package_info['package_id']}")
                        
                except Exception as e:
                    print(f"   ⚠️ Error reading {package_info_file}: {e}")
    
    # Sort packages by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    packages.sort(key=lambda x: priority_order.get(x.get("offline_priority", "medium"), 2))
    
    # Create enhanced catalog
    catalog = {
        "catalog_version": "2.0_enhanced",
        "quality_level": "maximum_768d",
        "created_date": datetime.now().isoformat(),
        "total_packages": len(packages),
        "total_size_bytes": total_size_bytes,
        "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
        "packages": packages,
        "enhancement_features": [
            "768d_embeddings",
            "smart_sentence_chunking", 
            "enhanced_keyword_extraction",
            "survival_synonym_expansion",
            "urgency_assessment",
            "domain_classification"
        ],
        "ios_requirements": {
            "min_ios_version": "14.0",
            "required_mlx": True,
            "required_storage_mb": round(total_size_bytes / (1024 * 1024) * 1.8, 1),  # 1.8x for 768d processing
            "swift_package_manager": True,
            "recommended_ram_mb": 1024  # For 768d embeddings
        },
        "download_strategy": {
            "recommended_order": [
                pkg["package_id"] for pkg in packages
            ],
            "bundle_options": {
                "essential": [pkg["package_id"] for pkg in packages if pkg["offline_priority"] in ["critical", "high"]],
                "complete": [pkg["package_id"] for pkg in packages]
            }
        }
    }
    
    # Save enhanced catalog
    catalog_file = rag_packages_dir / "catalog.json"
    with open(catalog_file, 'w') as f:
        json.dump(catalog, f, indent=2)
        
    print(f"\n📋 ENHANCED Catalog created: {catalog_file}")
    print(f"   Total packages: {len(packages)}")
    print(f"   Total size: {catalog['total_size_mb']}MB")
    print(f"   Quality: MAXIMUM (768d embeddings)")
    
    return catalog

if __name__ == "__main__":
    generate_enhanced_catalog() 