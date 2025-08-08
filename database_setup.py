# LandGPT Phase 1: Foundation & Data Collection
# File: database_setup.py

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import time
import random

class LandRecordDB:
    """Database manager for land records"""

    def __init__(self, db_path: str = "landgpt.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main land records table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS land_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district TEXT NOT NULL,
            tehsil TEXT NOT NULL,
            village TEXT NOT NULL,
            khasra_number TEXT NOT NULL,
            khata_number TEXT,
            owner_name TEXT,
            father_name TEXT,
            area_hectare REAL,
            area_bigha REAL,
            land_type TEXT,
            irrigation_status TEXT,
            crop_details TEXT,
            mutation_date TEXT,
            registry_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(district, tehsil, village, khasra_number)
        )
        ''')

        # Legal FAQs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS legal_faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT,
            tags TEXT,
            language TEXT DEFAULT 'hindi',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # User queries log
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            response TEXT,
            query_type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")

    def insert_land_record(self, record: Dict):
        """Insert a land record into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
            INSERT OR REPLACE INTO land_records
            (district, tehsil, village, khasra_number, khata_number,
             owner_name, father_name, area_hectare, area_bigha,
             land_type, irrigation_status, crop_details, mutation_date, registry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('district'), record.get('tehsil'), record.get('village'),
                record.get('khasra_number'), record.get('khata_number'),
                record.get('owner_name'), record.get('father_name'),
                record.get('area_hectare'), record.get('area_bigha'),
                record.get('land_type'), record.get('irrigation_status'),
                record.get('crop_details'), record.get('mutation_date'),
                record.get('registry_date')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error inserting record: {e}")
            return False
        finally:
            conn.close()

    def search_land_records(self, **kwargs) -> List[Dict]:
        """Search land records by various criteria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM land_records WHERE 1=1"
        params = []

        for key, value in kwargs.items():
            if value:
                query += f" AND {key} LIKE ?"
                params.append(f"%{value}%")

        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results


class BhulekhScraper:
    """Web scraper for Bhulekh UP data"""

    def __init__(self):
        self.base_url = "https://upbhulekh.gov.in"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_districts(self) -> List[str]:
        """Get list of districts from Bhulekh portal"""
        # For demo purposes, returning sample UP districts
        return [
            "Agra", "Aligarh", "Allahabad", "Ambedkar Nagar", "Amethi",
            "Amroha", "Auraiya", "Azamgarh", "Baghpat", "Bahraich",
            "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly"
        ]

    def get_tehsils(self, district: str) -> List[str]:
        """Get tehsils for a district"""
        # Sample tehsils (would be scraped from actual site)
        sample_tehsils = {
            "Agra": ["Agra", "Fatehabad", "Kheragarh", "Pinahat"],
            "Aligarh": ["Atrauli", "Gabhana", "Iglas", "Koil"],
            "Allahabad": ["Bara", "Handia", "Karchhana", "Koraon"]
        }
        return sample_tehsils.get(district, ["Sample Tehsil"])

    def get_villages(self, district: str, tehsil: str) -> List[str]:
        """Get villages for a tehsil"""
        # Sample villages (would be scraped from actual site)
        return ["Sample Village 1", "Sample Village 2", "Sample Village 3"]

    def scrape_khatauni(self, district: str, tehsil: str, village: str,
                       search_type: str = "khasra", search_value: str = "1") -> Dict:
        """
        Scrape khatauni data from Bhulekh portal
        This is a mock implementation - actual implementation would
        interact with the real website
        """

        # Simulate API delay
        time.sleep(random.uniform(1, 3))

        # Generate mock data for demonstration
        mock_record = {
            'district': district,
            'tehsil': tehsil,
            'village': village,
            'khasra_number': search_value,
            'khata_number': f"KH{random.randint(100, 999)}",
            'owner_name': "Sample Owner Name",
            'father_name': "Sample Father Name",
            'area_hectare': round(random.uniform(0.5, 5.0), 2),
            'area_bigha': round(random.uniform(1.0, 12.0), 2),
            'land_type': random.choice(["कृषि योग्य", "आवासीय", "बंजर"]),
            'irrigation_status': random.choice(["सिंचित", "असिंचित"]),
            'crop_details': random.choice(["गेहूं", "धान", "मक्का", "गन्ना"]),
            'mutation_date': "2023-01-15",
            'registry_date': "2022-12-10"
        }

        return mock_record

    def bulk_scrape(self, districts: List[str], max_records_per_district: int = 10):
        """Bulk scrape data for multiple districts"""
        db = LandRecordDB()
        total_scraped = 0

        for district in districts:
            print(f"🔄 Scraping {district}...")
            tehsils = self.get_tehsils(district)

            for tehsil in tehsils[:2]:  # Limit to 2 tehsils per district
                villages = self.get_villages(district, tehsil)

                for village in villages[:2]:  # Limit to 2 villages per tehsil
                    for khasra_num in range(1, min(max_records_per_district//4 + 1, 6)):
                        try:
                            record = self.scrape_khatauni(district, tehsil, village,
                                                        "khasra", str(khasra_num))
                            if db.insert_land_record(record):
                                total_scraped += 1
                                print(f"  ✅ Scraped Khasra {khasra_num} from {village}")
                        except Exception as e:
                            print(f"  ❌ Error scraping {district}/{tehsil}/{village}: {e}")

        print(f"🎉 Total records scraped: {total_scraped}")


class LegalFAQLoader:
    """Load legal FAQs related to land records"""

    def __init__(self):
        self.db = LandRecordDB()

    def load_sample_faqs(self):
        """Load sample land-related legal FAQs"""

        sample_faqs = [
            {
                'question': 'Mutation ke liye application kaise karein?',
                'answer': '''म्यूटेशन के लिए आवेदन की प्रक्रिया:
1. जिला कलेक्ट्रेट या तहसील कार्यालय जाएं
2. म्यूटेशन आवेदन फॉर्म भरें
3. आवश्यक दस्तावेज संलग्न करें: बिक्री पत्र, रसीद, आधार कार्ड
4. निर्धारित शुल्क का भुगतान करें
5. आवेदन जमा करने के बाद रसीद प्राप्त करें
6. 30 दिन में प्रक्रिया पूरी हो जाती है''',
                'category': 'mutation',
                'tags': 'mutation,application,process',
                'language': 'hindi'
            },
            {
                'question': 'Khasra number kya hota hai?',
                'answer': '''खसरा नंबर का मतलब:
खसरा नंबर भूमि के एक टुकड़े का विशिष्ट पहचान संख्या है। यह:
- हर जमीन के प्लॉट का अलग नंबर होता है
- सरकारी रिकॉर्ड में जमीन की पहचान के लिए उपयोग होता है
- खतौनी में दर्ज होता है
- जमीन खरीदने-बेचने में जरूरी है''',
                'category': 'basic_terms',
                'tags': 'khasra,land_records,identification',
                'language': 'hindi'
            },
            {
                'question': 'Registry ke documents kya chahiye?',
                'answer': '''रजिस्ट्री के लिए आवश्यक दस्तावेज:
1. मूल बिक्री पत्र (Sale Deed)
2. पुराना रजिस्ट्री दस्तावेज
3. खसरा/खतौनी की प्रति
4. आधार कार्ड (खरीदार और बेचने वाले का)
5. PAN कार्ड
6. NOC (यदि कोई लोन है)
7. फोटो
8. रजिस्ट्री फीस की रसीद''',
                'category': 'registry',
                'tags': 'registry,documents,required',
                'language': 'hindi'
            }
        ]

        for faq in sample_faqs:
            self.insert_faq(faq)

    def insert_faq(self, faq: Dict):
        """Insert FAQ into database"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO legal_faqs (question, answer, category, tags, language)
        VALUES (?, ?, ?, ?, ?)
        ''', (faq['question'], faq['answer'], faq['category'],
              faq['tags'], faq['language']))

        conn.commit()
        conn.close()


# Main execution
if __name__ == "__main__":
    print("🚀 Starting LandGPT Phase 1 Setup...")

    # Initialize database
    db = LandRecordDB()

    # Load sample FAQs
    print("📚 Loading legal FAQs...")
    faq_loader = LegalFAQLoader()
    faq_loader.load_sample_faqs()

    # Initialize scraper and get sample data
    print("🔍 Setting up scraper...")
    scraper = BhulekhScraper()

    # Get sample districts for scraping
    districts = scraper.get_districts()[:3]  # Start with 3 districts

    # Start bulk scraping (mock data for now)
    print("🌐 Starting bulk scraping...")
    scraper.bulk_scrape(districts, max_records_per_district=8)

    # Test database queries
    print("\n📊 Testing database queries...")

    # Search for records
    results = db.search_land_records(district="Agra")
    print(f"Found {len(results)} records in Agra")

    if results:
        print(f"Sample record: {results[0]['owner_name']} - Khasra {results[0]['khasra_number']}")

    print("✅ Phase 1 setup completed!")
    print("\nNext steps:")
    print("1. Replace mock scraping with real Bhulekh integration")
    print("2. Add more comprehensive FAQs")
    print("3. Set up Phase 2: NLP and RAG system")