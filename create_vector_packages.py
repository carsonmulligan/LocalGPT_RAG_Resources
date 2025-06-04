#!/usr/bin/env python3
"""
Create Vector Database Packages for iOS Distribution
Processes PDFs into pre-vectorized packages that can be served via the RAG API.
"""

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
import mlx.core as mx
from datetime import datetime
import hashlib

# Import our RAG system
from fishing_mlx_rag import FishingVectorDB, EmbeddingModel

class VectorPackageCreator:
    def __init__(self, output_dir: str = "vector_packages"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.embedding_model = EmbeddingModel()
        
    def create_package_from_pdf(self, pdf_path: str, package_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete vector package from a PDF."""
        print(f"🔄 Creating vector package: {package_id}")
        
        # Create package directory
        package_dir = self.output_dir / package_id
        package_dir.mkdir(exist_ok=True)
        
        # Create vector database
        vdb = FishingVectorDB()
        vdb.create_from_pdf(pdf_path)
        
        # Save vector database
        vdb_file = package_dir / f"{package_id}.vdb.npz"
        vdb.save_vdb(str(vdb_file))
        
        # Create embeddings metadata
        embeddings_info = {
            "embedding_model": "BAAI/bge-small-en",
            "chunk_size": 1000,
            "overlap": 200,
            "num_chunks": len(vdb.content),
            "embedding_dim": vdb.embeddings.shape[1],
            "total_embeddings": vdb.embeddings.shape[0]
        }
        
        # Create iOS-optimized index
        ios_index = self.create_ios_index(vdb, package_id)
        ios_index_file = package_dir / f"{package_id}_ios.index.json"
        with open(ios_index_file, 'w') as f:
            json.dump(ios_index, f, indent=2)
        
        # Calculate file sizes
        vdb_size = os.path.getsize(vdb_file)
        index_size = os.path.getsize(ios_index_file)
        
        # Create package metadata
        package_info = {
            "package_id": package_id,
            "name": metadata.get("name", package_id.replace("_", " ").title()),
            "description": metadata.get("description", "Survival knowledge package"),
            "version": "1.0",
            "created_date": datetime.now().isoformat(),
            "source_pdf": Path(pdf_path).name,
            "vector_database": {
                "file": f"{package_id}.vdb.npz",
                "size_bytes": vdb_size,
                "format": "mlx_npz",
                "compression": "auto"
            },
            "ios_index": {
                "file": f"{package_id}_ios.index.json", 
                "size_bytes": index_size,
                "format": "json",
                "optimized_for": "swift_integration"
            },
            "embeddings": embeddings_info,
            "offline_priority": metadata.get("priority", "medium"),
            "category": metadata.get("category", "survival"),
            "tags": metadata.get("tags", []),
            "checksum": {
                "vdb": self.calculate_checksum(vdb_file),
                "index": self.calculate_checksum(ios_index_file)
            }
        }
        
        # Save package metadata
        package_info_file = package_dir / "package_info.json"
        with open(package_info_file, 'w') as f:
            json.dump(package_info, f, indent=2)
            
        print(f"✅ Package created: {package_dir}")
        print(f"   Vector DB: {vdb_size/1024:.1f}KB")
        print(f"   iOS Index: {index_size/1024:.1f}KB")
        print(f"   Total chunks: {len(vdb.content)}")
        
        return package_info
    
    def create_ios_index(self, vdb: FishingVectorDB, package_id: str) -> Dict[str, Any]:
        """Create iOS-optimized search index."""
        # Extract keywords and create searchable index
        chunks_data = []
        for i, chunk in enumerate(vdb.content):
            # Extract key phrases for quick keyword search
            words = chunk.lower().split()
            keywords = [word.strip('.,!?()[]{}') for word in words if len(word) > 3]
            
            chunks_data.append({
                "chunk_id": i,
                "text": chunk,
                "keywords": list(set(keywords[:20])),  # Top 20 unique keywords
                "length": len(chunk),
                "preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
            })
        
        # Create keyword lookup for fast iOS search
        keyword_lookup = {}
        for i, chunk_data in enumerate(chunks_data):
            for keyword in chunk_data["keywords"]:
                if keyword not in keyword_lookup:
                    keyword_lookup[keyword] = []
                keyword_lookup[keyword].append(i)
        
        return {
            "package_id": package_id,
            "format_version": "1.0",
            "optimized_for": "ios_swift",
            "chunks": chunks_data,
            "keyword_lookup": keyword_lookup,
            "search_config": {
                "min_keyword_length": 3,
                "max_results": 10,
                "relevance_threshold": 0.1
            },
            "ios_integration": {
                "swift_compatible": True,
                "core_ml_ready": True,
                "memory_efficient": True
            }
        }
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum for file integrity."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def create_catalog(self, packages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create master catalog for all packages."""
        total_size = sum(
            pkg["vector_database"]["size_bytes"] + pkg["ios_index"]["size_bytes"] 
            for pkg in packages
        )
        
        catalog = {
            "catalog_version": "1.0",
            "created_date": datetime.now().isoformat(),
            "total_packages": len(packages),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "packages": packages,
            "ios_requirements": {
                "min_ios_version": "14.0",
                "required_mlx": True,
                "required_storage_mb": round(total_size / (1024 * 1024) * 1.5, 1),  # 1.5x for processing
                "swift_package_manager": True
            },
            "download_strategy": {
                "recommended_order": [
                    pkg["package_id"] for pkg in 
                    sorted(packages, key=lambda x: {
                        "critical": 0, "high": 1, "medium": 2, "low": 3
                    }.get(x["offline_priority"], 2))
                ],
                "bundle_options": {
                    "essential": [pkg["package_id"] for pkg in packages if pkg["offline_priority"] in ["critical", "high"]],
                    "complete": [pkg["package_id"] for pkg in packages]
                }
            }
        }
        
        # Save catalog
        catalog_file = self.output_dir / "catalog.json"
        with open(catalog_file, 'w') as f:
            json.dump(catalog, f, indent=2)
            
        print(f"📋 Catalog created: {catalog_file}")
        print(f"   Total packages: {len(packages)}")
        print(f"   Total size: {catalog['total_size_mb']}MB")
        
        return catalog

def main():
    parser = argparse.ArgumentParser(description="Create Vector Database Packages for iOS")
    parser.add_argument("--input-dir", default="pdfs", help="Directory containing PDF files")
    parser.add_argument("--output-dir", default="vector_packages", help="Output directory for packages")
    parser.add_argument("--config", help="JSON config file with package metadata")
    
    args = parser.parse_args()
    
    print("📦 Creating Vector Database Packages for iOS")
    print("=" * 60)
    
    creator = VectorPackageCreator(args.output_dir)
    
    # Default package configurations
    default_config = {
        "fishingguide1.pdf": {
            "package_id": "fishing_basics",
            "name": "Fishing Basics & Techniques",
            "description": "Essential fishing techniques, knot tying, and equipment guide",
            "priority": "high",
            "category": "survival_skills",
            "tags": ["fishing", "knots", "survival", "food_procurement"]
        }
    }
    
    # Load custom config if provided
    config = default_config
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Process all PDFs in input directory
    input_dir = Path(args.input_dir)
    packages = []
    
    for pdf_file in input_dir.glob("*.pdf"):
        pdf_name = pdf_file.name
        if pdf_name in config:
            package_info = creator.create_package_from_pdf(
                str(pdf_file), 
                config[pdf_name]["package_id"],
                config[pdf_name]
            )
            packages.append(package_info)
        else:
            print(f"⚠️ No config found for {pdf_name}, skipping...")
    
    # Create master catalog
    if packages:
        catalog = creator.create_catalog(packages)
        
        print(f"\n🎯 Vector packages ready for iOS integration!")
        print(f"📁 Output directory: {args.output_dir}")
        print(f"📊 Ready to serve via RAG API")
    else:
        print("❌ No packages created. Check your PDF files and configuration.")

if __name__ == "__main__":
    main() 
