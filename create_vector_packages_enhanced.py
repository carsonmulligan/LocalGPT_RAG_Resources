#!/usr/bin/env python3
"""
Enhanced Vector Database Packages for iOS Distribution - MAXIMUM QUALITY
Processes PDFs into pre-vectorized packages with 768d embeddings and smart chunking.
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
from datetime import datetime
import hashlib
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
import PyPDF2
from sentence_transformers import SentenceTransformer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class EnhancedEmbeddingModel:
    """Enhanced embedding model using sentence-transformers for maximum quality."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        print(f"🔄 Loading high-quality embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"✅ Model loaded: {self.embedding_dim}d embeddings")
        
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to high-quality embeddings."""
        return self.model.encode(texts, show_progress_bar=True)

class SurvivalTextProcessor:
    """Enhanced text processing specifically optimized for survival content."""
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Survival-specific terms to always preserve
        self.survival_keywords = {
            'fire', 'water', 'shelter', 'food', 'survival', 'emergency', 'first', 'aid',
            'knot', 'rope', 'fishing', 'hunt', 'plant', 'medical', 'wound', 'bleeding',
            'hypothermia', 'dehydration', 'signaling', 'rescue', 'navigation', 'compass',
            'map', 'safety', 'danger', 'poison', 'edible', 'toxic', 'military', 'combat',
            'weapon', 'defense', 'evasion', 'camouflage', 'equipment', 'gear', 'tool'
        }
        
        # Remove survival terms from stop words
        self.stop_words = self.stop_words - self.survival_keywords
        
        # Survival-specific synonyms for query expansion
        self.survival_synonyms = {
            'fire': ['flame', 'ignition', 'spark', 'tinder', 'kindling', 'combustion'],
            'water': ['hydration', 'liquid', 'purification', 'filtration', 'H2O'],
            'shelter': ['housing', 'protection', 'cover', 'refuge', 'dwelling'],
            'food': ['nutrition', 'sustenance', 'ration', 'meal', 'hunting', 'foraging'],
            'medical': ['health', 'treatment', 'care', 'healing', 'medicine'],
            'emergency': ['crisis', 'urgent', 'critical', 'disaster', 'rescue'],
            'knot': ['rope', 'tie', 'binding', 'lashing', 'cordage'],
            'navigation': ['direction', 'compass', 'map', 'orientation', 'GPS']
        }
    
    def extract_enhanced_keywords(self, text: str) -> List[str]:
        """Extract high-quality keywords with survival-specific optimization."""
        # Clean and tokenize
        words = word_tokenize(text.lower())
        
        # Filter and process
        keywords = []
        for word in words:
            # Remove punctuation and check length
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) < 3:
                continue
                
            # Skip stop words (except survival terms)
            if clean_word in self.stop_words:
                continue
                
            # Stem word but preserve original survival terms
            if clean_word in self.survival_keywords:
                keywords.append(clean_word)
            else:
                stemmed = self.stemmer.stem(clean_word)
                if len(stemmed) >= 3:
                    keywords.append(stemmed)
        
        # Add survival synonyms for key terms
        enhanced_keywords = set(keywords)
        for keyword in keywords:
            if keyword in self.survival_synonyms:
                enhanced_keywords.update(self.survival_synonyms[keyword])
        
        return list(enhanced_keywords)[:25]  # Top 25 enhanced keywords
    
    def smart_chunk_text(self, text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
        """Intelligent chunking that preserves sentence boundaries and instruction sequences."""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Check if adding this sentence would exceed max_chars
            if len(current_chunk) + len(sentence) > max_chars and current_chunk:
                # Save current chunk
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                if overlap > 0 and len(current_chunk) > overlap:
                    # Try to preserve context with overlap
                    overlap_text = current_chunk[-overlap:]
                    # Find sentence boundary in overlap
                    sentences_in_overlap = sent_tokenize(overlap_text)
                    if len(sentences_in_overlap) > 1:
                        current_chunk = sentences_in_overlap[-1] + " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

class EnhancedVectorDB:
    """Enhanced vector database with maximum quality embeddings and smart processing."""
    
    def __init__(self, embedding_model: EnhancedEmbeddingModel = None):
        self.embedding_model = embedding_model or EnhancedEmbeddingModel()
        self.text_processor = SurvivalTextProcessor()
        self.content = []
        self.embeddings = None
        self.metadata = []
    
    def create_from_pdf(self, pdf_path: str):
        """Create vector database from PDF with enhanced processing."""
        print(f"🔄 Processing PDF: {pdf_path}")
        
        # Extract text from PDF
        text = self._extract_pdf_text(pdf_path)
        
        # Smart chunking
        chunks = self.text_processor.smart_chunk_text(text, max_chars=1000, overlap=200)
        
        print(f"📄 Extracted {len(chunks)} intelligent chunks")
        
        # Create embeddings
        print("🧠 Creating high-quality embeddings...")
        embeddings = self.embedding_model.encode(chunks)
        
        # Store results
        self.content = chunks
        self.embeddings = embeddings
        self.metadata = [{"chunk_id": i, "source": pdf_path} for i in range(len(chunks))]
        
        print(f"✅ Vector database created: {len(chunks)} chunks, {embeddings.shape[1]}d embeddings")
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract and clean text from PDF."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"⚠️ Error reading PDF {pdf_path}: {e}")
            return ""
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]]', '', text)  # Remove special chars
        
        return text.strip()
    
    def save_vdb(self, filepath: str):
        """Save vector database to file."""
        np.savez_compressed(filepath, 
                          embeddings=self.embeddings,
                          content=np.array(self.content, dtype=object),
                          metadata=np.array(self.metadata, dtype=object))

class EnhancedVectorPackageCreator:
    """Enhanced package creator with maximum quality optimizations."""
    
    def __init__(self, output_dir: str = "vector_packages_enhanced"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.embedding_model = EnhancedEmbeddingModel()
        self.text_processor = SurvivalTextProcessor()
        
    def create_package_from_pdf(self, pdf_path: str, package_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete enhanced vector package from a PDF."""
        print(f"🔄 Creating ENHANCED vector package: {package_id}")
        
        # Create package directory
        package_dir = self.output_dir / package_id
        package_dir.mkdir(exist_ok=True)
        
        # Create enhanced vector database
        vdb = EnhancedVectorDB(self.embedding_model)
        vdb.create_from_pdf(pdf_path)
        
        # Save vector database
        vdb_file = package_dir / f"{package_id}.vdb.npz"
        vdb.save_vdb(str(vdb_file))
        
        # Create enhanced embeddings metadata
        embeddings_info = {
            "embedding_model": self.embedding_model.model_name,
            "embedding_quality": "maximum_768d",
            "chunk_size": 1000,
            "overlap": 200,
            "num_chunks": len(vdb.content),
            "embedding_dim": vdb.embeddings.shape[1],
            "total_embeddings": vdb.embeddings.shape[0],
            "chunking_strategy": "smart_sentence_boundary",
            "keyword_extraction": "enhanced_survival_optimized"
        }
        
        # Create enhanced iOS-optimized index
        ios_index = self.create_enhanced_ios_index(vdb, package_id)
        ios_index_file = package_dir / f"{package_id}_ios.index.json"
        with open(ios_index_file, 'w') as f:
            json.dump(ios_index, f, indent=2)
        
        # Calculate file sizes
        vdb_size = os.path.getsize(vdb_file)
        index_size = os.path.getsize(ios_index_file)
        
        # Create enhanced package metadata
        package_info = {
            "package_id": package_id,
            "name": metadata.get("name", package_id.replace("_", " ").title()),
            "description": metadata.get("description", "Enhanced survival knowledge package"),
            "version": "2.0_enhanced",
            "created_date": datetime.now().isoformat(),
            "source_pdf": Path(pdf_path).name,
            "quality_level": "maximum",
            "vector_database": {
                "file": f"{package_id}.vdb.npz",
                "size_bytes": vdb_size,
                "format": "mlx_npz",
                "compression": "auto",
                "quality": "768d_maximum"
            },
            "ios_index": {
                "file": f"{package_id}_ios.index.json", 
                "size_bytes": index_size,
                "format": "json",
                "optimized_for": "swift_integration_enhanced",
                "features": ["smart_keywords", "survival_synonyms", "stemming"]
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
            
        print(f"✅ ENHANCED Package created: {package_dir}")
        print(f"   Vector DB: {vdb_size/1024:.1f}KB (768d embeddings)")
        print(f"   iOS Index: {index_size/1024:.1f}KB (enhanced keywords)")
        print(f"   Total chunks: {len(vdb.content)} (smart boundaries)")
        
        return package_info
    
    def create_enhanced_ios_index(self, vdb: EnhancedVectorDB, package_id: str) -> Dict[str, Any]:
        """Create enhanced iOS-optimized search index with survival-specific features."""
        chunks_data = []
        
        for i, chunk in enumerate(vdb.content):
            # Enhanced keyword extraction
            keywords = self.text_processor.extract_enhanced_keywords(chunk)
            
            # Create survival-specific metadata
            chunk_metadata = {
                "contains_instructions": bool(re.search(r'\d+\.\s|\bstep\b|\bhow\s+to\b', chunk.lower())),
                "urgency_level": self._assess_urgency(chunk),
                "survival_domains": self._identify_domains(chunk)
            }
            
            chunks_data.append({
                "chunk_id": i,
                "text": chunk,
                "keywords": keywords,
                "enhanced_metadata": chunk_metadata,
                "length": len(chunk),
                "preview": chunk[:150] + "..." if len(chunk) > 150 else chunk
            })
        
        # Create enhanced keyword lookup with synonyms
        keyword_lookup = {}
        for i, chunk_data in enumerate(chunks_data):
            for keyword in chunk_data["keywords"]:
                if keyword not in keyword_lookup:
                    keyword_lookup[keyword] = []
                keyword_lookup[keyword].append(i)
        
        return {
            "package_id": package_id,
            "format_version": "2.0_enhanced",
            "optimized_for": "ios_swift_maximum_quality",
            "chunks": chunks_data,
            "keyword_lookup": keyword_lookup,
            "enhanced_features": {
                "smart_chunking": True,
                "survival_synonyms": True,
                "keyword_stemming": True,
                "urgency_assessment": True,
                "domain_classification": True
            },
            "search_config": {
                "min_keyword_length": 3,
                "max_results": 15,
                "relevance_threshold": 0.05,
                "synonym_expansion": True
            },
            "ios_integration": {
                "swift_compatible": True,
                "core_ml_ready": True,
                "memory_efficient": True,
                "quality_optimized": True
            }
        }
    
    def _assess_urgency(self, text: str) -> str:
        """Assess urgency level of survival content."""
        urgent_terms = ['emergency', 'critical', 'immediate', 'danger', 'life', 'death', 'urgent']
        high_terms = ['important', 'essential', 'vital', 'must', 'should', 'warning']
        
        text_lower = text.lower()
        
        if any(term in text_lower for term in urgent_terms):
            return "critical"
        elif any(term in text_lower for term in high_terms):
            return "high"
        else:
            return "normal"
    
    def _identify_domains(self, text: str) -> List[str]:
        """Identify survival domains present in the text."""
        domains = []
        text_lower = text.lower()
        
        domain_keywords = {
            "medical": ["first aid", "medical", "wound", "bleeding", "cpr", "health"],
            "fire": ["fire", "flame", "ignition", "spark", "tinder"],
            "water": ["water", "purification", "hydration", "filter"],
            "shelter": ["shelter", "protection", "cover", "dwelling"],
            "food": ["food", "hunting", "fishing", "foraging", "edible"],
            "navigation": ["navigation", "compass", "map", "direction"],
            "signaling": ["signal", "rescue", "help", "sos"],
            "knots": ["knot", "rope", "tie", "cord"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                domains.append(domain)
        
        return domains
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum for file integrity."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Create ENHANCED Vector Database Packages for iOS")
    parser.add_argument("--input-dir", default="pdfs", help="Directory containing PDF files")
    parser.add_argument("--output-dir", default="vector_packages_enhanced", help="Output directory for enhanced packages")
    
    args = parser.parse_args()
    
    print("🚀 Creating ENHANCED Vector Database Packages for iOS")
    print("=" * 70)
    print("🎯 MAXIMUM QUALITY MODE: 768d embeddings + Smart Processing")
    print("=" * 70)
    
    creator = EnhancedVectorPackageCreator(args.output_dir)
    
    # Load existing configuration from current rag_packages
    config = {}
    rag_packages_dir = Path("rag_packages")
    if rag_packages_dir.exists():
        for package_dir in rag_packages_dir.iterdir():
            if package_dir.is_dir() and (package_dir / "package_info.json").exists():
                with open(package_dir / "package_info.json", 'r') as f:
                    pkg_info = json.load(f)
                    config[pkg_info["source_pdf"]] = {
                        "package_id": pkg_info["package_id"],
                        "name": pkg_info["name"],
                        "description": pkg_info["description"],
                        "priority": pkg_info["offline_priority"],
                        "category": pkg_info["category"],
                        "tags": pkg_info["tags"]
                    }
    
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
    
    print(f"\n🎯 ENHANCED Vector packages created!")
    print(f"📁 Output directory: {args.output_dir}")
    print(f"🚀 MAXIMUM QUALITY: 768d embeddings + Smart Processing")
    print(f"📊 Ready for superior RAG performance!")

if __name__ == "__main__":
    main() 