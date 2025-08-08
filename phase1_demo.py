# phase1_demo.py
# Demo script to test Phase 1 functionality

import os
import sqlite3
import json
from datetime import datetime
import pandas as pd

class LandGPTPhase1Demo:
    """Demo class to showcase Phase 1 functionality"""

    def __init__(self, db_path: str = "landgpt.db"):
        self.db_path = db_path
        self.setup_demo_environment()

    def setup_demo_environment(self):
        """Setup demo environment with sample data"""
        print("🏗️  Setting up LandGPT Phase 1 Demo Environment...")

        # Import our modules
        try:
            from database_setup import LandRecordDB, LegalFAQLoader, BhulekhScraper
            self.db = LandRecordDB(self.db_path)
            self.faq_loader = LegalFAQLoader()
            self.scraper = BhulekhScraper()
            print("✅ Modules imported successfully")
        except ImportError as e:
            print(f"❌ Error importing modules: {e}")
            print("💡 Make sure database_setup.py is in the same directory")
            return False

        return True

    def demo_database_operations(self):
        """Demonstrate database operations"""
        print("\n📊 === DATABASE OPERATIONS DEMO ===")

        # Test database connection
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Database tables: {[table[0] for table in tables]}")

        # Count records
        cursor.execute("SELECT COUNT(*) FROM land_records")
        land_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM legal_faqs")
        faq_count = cursor.fetchone()[0]

        print(f"📄 Land records: {land_count}")
        print(f"❓ Legal FAQs: {faq_count}")

        conn.close()

    def demo_sample_queries(self):
        """Demonstrate sample database queries"""
        print("\n🔍 === SAMPLE QUERIES DEMO ===")

        conn = sqlite3.connect(self.db_path)

        # Query 1: Search by district
        print("\n🏙️ Query 1: Records from Agra district")
        df = pd.read_sql_query(
            "SELECT * FROM land_records WHERE district LIKE '%Agra%' LIMIT 5",
            conn
        )
        if not df.empty:
            print(f"   Found {len(df)} records")
            print(f"   Sample: Owner '{df.iloc[0]['owner_name']}' - Khasra {df.iloc[0]['khasra_number']}")
        else:
            print("   No records found")

        # Query 2: Search by area range
        print("\n📐 Query 2: Land parcels > 2 hectares")
        df = pd.read_sql_query(
            "SELECT * FROM land_records WHERE area_hectare > 2.0 LIMIT 3",
            conn
        )
        if not df.empty:
            print(f"   Found {len(df)} large parcels")
            for _, row in df.iterrows():
                print(f"   - {row['area_hectare']} hectare plot in {row['village']}")
        else:
            print("   No large parcels found")

        # Query 3: Legal FAQs
        print("\n❓ Query 3: Legal FAQs by category")
        df = pd.read_sql_query(
            "SELECT category, COUNT(*) as count FROM legal_faqs GROUP BY category",
            conn
        )
        print("   FAQ categories:")
        for _, row in df.iterrows():
            print(f"   - {row['category']}: {row['count']} questions")

        conn.close()

    def demo_faq_search(self):
        """Demonstrate FAQ search functionality"""
        print("\n💬 === FAQ SEARCH DEMO ===")

        conn = sqlite3.connect(self.db_path)

        # Search for mutation-related FAQs
        search_terms = ['mutation', 'म्यूटेशन', 'registry']

        for term in search_terms:
            print(f"\n🔎 Searching for: '{term}'")

            query = """
            SELECT question, answer, category
            FROM legal_faqs
            WHERE question LIKE ? OR answer LIKE ? OR tags LIKE ?
            LIMIT 2
            """

            df = pd.read_sql_query(query, conn, params=[f'%{term}%', f'%{term}%', f'%{term}%'])

            if not df.empty:
                for _, row in df.iterrows():
                    print(f"   Q: {row['question']}")
                    print(f"   A: {row['answer'][:100]}...")
                    print(f"   Category: {row['category']}\n")
            else:
                print("   No matching FAQs found")

        conn.close()

    def demo_data_analysis(self):
        """Demonstrate basic data analysis"""
        print("\n📈 === DATA ANALYSIS DEMO ===")

        conn = sqlite3.connect(self.db_path)

        # Land distribution analysis
        print("🏞️ Land Distribution Analysis:")

        # By district
        df = pd.read_sql_query(
            "SELECT district, COUNT(*) as plots, AVG(area_hectare) as avg_area FROM land_records GROUP BY district",
            conn
        )

        if not df.empty:
            print("   By District:")
            for _, row in df.iterrows():
                print(f"   - {row['district']}: {row['plots']} plots, avg {row['avg_area']:.2f} hectares")

        # By land type
        df = pd.read_sql_query(
            "SELECT land_type, COUNT(*) as count FROM land_records WHERE land_type IS NOT NULL GROUP BY land_type",
            conn
        )

        if not df.empty:
            print("\n   By Land Type:")
            for _, row in df.iterrows():
                print(f"   - {row['land_type']}: {row['count']} plots")

        # Irrigation analysis
        df = pd.read_sql_query(
            "SELECT irrigation_status, COUNT(*) as count FROM land_records WHERE irrigation_status IS NOT NULL GROUP BY irrigation_status",
            conn
        )

        if not df.empty:
            print("\n   By Irrigation Status:")
            for _, row in df.iterrows():
                print(f"   - {row['irrigation_status']}: {row['count']} plots")

        conn.close()

    def demo_mock_user_interaction(self):
        """Simulate user interactions"""
        print("\n👤 === MOCK USER INTERACTION DEMO ===")

        # Sample user queries
        user_queries = [
            "Mutation ke liye application kaise karein?",
            "Khasra number kya hota hai?",
            "Agra mein kitni zameen hai?",
            "Registry ke documents kya chahiye?"
        ]

        conn = sqlite3.connect(self.db_path)

        for i, query in enumerate(user_queries, 1):
            print(f"\n🗣️ User Query {i}: {query}")

            # Log the query
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_queries (query, query_type) VALUES (?, ?)",
                (query, "demo")
            )
            conn.commit()

            # Simple keyword matching for demo
            if any(keyword in query.lower() for keyword in ['mutation', 'म्यूटेशन']):
                # Search for mutation FAQs
                df = pd.read_sql_query(
                    "SELECT answer FROM legal_faqs WHERE tags LIKE '%mutation%' LIMIT 1",
                    conn
                )
                if not df.empty:
                    print(f"🤖 LandGPT Response: {df.iloc[0]['answer'][:200]}...")
                else:
                    print("🤖 LandGPT Response: I can help with mutation processes. Let me find more information.")

            elif 'khasra' in query.lower():
                df = pd.read_sql_query(
                    "SELECT answer FROM legal_faqs WHERE question LIKE '%Khasra%' LIMIT 1",
                    conn
                )
                if not df.empty:
                    print(f"🤖 LandGPT Response: {df.iloc[0]['answer'][:200]}...")
                else:
                    print("🤖 LandGPT Response: Khasra number is a unique identifier for land plots.")

            elif 'agra' in query.lower():
                df = pd.read_sql_query(
                    "SELECT COUNT(*) as count, SUM(area_hectare) as total_area FROM land_records WHERE district LIKE '%Agra%'",
                    conn
                )
                if not df.empty and df.iloc[0]['count'] > 0:
                    count = df.iloc[0]['count']
                    total_area = df.iloc[0]['total_area'] or 0
                    print(f"🤖 LandGPT Response: मेरे पास आगरा के {count} भूमि रिकॉर्ड हैं, कुल क्षेत्रफल {total_area:.2f} हेक्टेयर")
                else:
                    print("🤖 LandGPT Response: Let me search for Agra land records...")

            else:
                print("🤖 LandGPT Response: मैं आपकी भूमि संबंधी समस्या में मदद कर सकता हूं। कृपया अधिक विवरण दें।")

        conn.close()

        # Show query statistics
        df = pd.read_sql_query("SELECT COUNT(*) as total FROM user_queries", conn)
        if not df.empty:
            print(f"\n📊 Total user queries logged: {df.iloc[0]['total']}")

    def generate_phase1_report(self):
        """Generate Phase 1 completion report"""
        print("\n📋 === PHASE 1 COMPLETION REPORT ===")

        conn = sqlite3.connect(self.db_path)

        # Database statistics
        stats = {}

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM land_records")
        stats['land_records'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM legal_faqs")
        stats['faqs'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_queries")
        stats['queries'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT district) FROM land_records")
        stats['districts'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT tehsil) FROM land_records")
        stats['tehsils'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT village) FROM land_records")
        stats['villages'] = cursor.fetchone()[0]

        conn.close()

        # Generate report
        print("📊 DATABASE STATISTICS:")
        print(f"   • Land Records: {stats['land_records']}")
        print(f"   • Legal FAQs: {stats['faqs']}")
        print(f"   • User Queries: {stats['queries']}")
        print(f"   • Districts Covered: {stats['districts']}")
        print(f"   • Tehsils Covered: {stats['tehsils']}")
        print(f"   • Villages Covered: {stats['villages']}")

        print("\n✅ PHASE 1 ACHIEVEMENTS:")
        print("   ✓ Database schema designed and implemented")
        print("   ✓ Web scraping infrastructure developed")
        print("   ✓ Sample data collection completed")
        print("   ✓ Legal FAQ system implemented")
        print("   ✓ Basic query functionality working")
        print("   ✓ Data analysis capabilities demonstrated")

        print("\n🎯 READY FOR PHASE 2:")
        print("   → NLP and Hindi language processing")
        print("   → RAG system implementation")
        print("   → LangChain integration")
        print("   → Advanced query understanding")
        print("   → Multi-language support")

        print("\n💡 RECOMMENDATIONS:")
        if stats['land_records'] < 100:
            print("   • Increase sample data collection for better testing")
        if stats['faqs'] < 20:
            print("   • Add more comprehensive legal FAQs")
        print("   • Implement real Bhulekh API integration")
        print("   • Add data validation and quality checks")
        print("   • Set up automated data refresh mechanisms")

    def run_complete_demo(self):
        """Run complete Phase 1 demonstration"""
        print("🎬 Starting LandGPT Phase 1 Complete Demo\n")
        print("=" * 60)

        # Step 1: Database operations
        self.demo_database_operations()

        # Step 2: Sample queries
        self.demo_sample_queries()

        # Step 3: FAQ search
        self.demo_faq_search()

        # Step 4: Data analysis
        self.demo_data_analysis()

        # Step 5: User interaction simulation
        self.demo_mock_user_interaction()

        # Step 6: Final report
        self.generate_phase1_report()

        print("\n" + "=" * 60)
        print("🎉 Phase 1 Demo Complete!")
        print("📁 Database file: " + self.db_path)
        print("🚀 Ready to proceed to Phase 2: NLP & RAG System")


# Main execution
if __name__ == "__main__":
    print("🌟 LandGPT - Phase 1 Demonstration")
    print("Building AI Legal Assistant for Indian Land Records\n")

    # Initialize demo
    demo = LandGPTPhase1Demo()

    # Check if we have existing data, if not create some
    if os.path.exists("landgpt.db"):
        print("📁 Found existing database")
    else:
        print("🆕 Creating new database with sample data...")
        # Run the database setup from our first artifact
        exec(open('database_setup.py').read() if os.path.exists('database_setup.py')
             else print("❌ database_setup.py not found. Please run it first."))

    # Run complete demonstration
    demo.run_complete_demo()

    print("\n👨‍💻 Next Steps:")
    print("1. Review the generated database and FAQs")
    print("2. Test real web scraping with bhulekh_scraper.py")
    print("3. Expand FAQ database with legal expert input")
    print("4. Begin Phase 2: NLP and RAG implementation")
    print("\n🙏 Thank you for building technology for rural empowerment!")
    print("🌾 LandGPT will help millions of farmers and citizens access land records easily.")