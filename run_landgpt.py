# run_landgpt.py - Simple script to run LandGPT Phase 1

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    packages = [
        "requests", "beautifulsoup4", "pandas", "numpy",
        "selenium", "webdriver-manager", "loguru", "fake-useragent"
    ]

    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def check_files():
    """Check if required files exist"""
    required_files = ["database_setup.py", "phase1_demo.py"]
    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n💡 Please copy the code from the artifacts into these files")
        return False

    print("✅ All required files found")
    return True

def setup_database():
    """Run database setup"""
    print("\n🗄️ Setting up database...")
    try:
        import database_setup
        print("✅ Database setup completed")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def run_demo():
    """Run the demo"""
    print("\n🎬 Running demo...")
    try:
        import phase1_demo
        demo = phase1_demo.LandGPTPhase1Demo()
        demo.run_complete_demo()
        return True
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def interactive_query():
    """Simple interactive query system"""
    import sqlite3
    import pandas as pd

    print("\n💬 LandGPT Interactive Query System")
    print("Enter 'quit' to exit")

    conn = sqlite3.connect("landgpt.db")

    while True:
        user_input = input("\n🗣️ Ask about land records: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            break

        # Simple keyword-based responses
        if any(word in user_input.lower() for word in ['agra', 'आगरा']):
            df = pd.read_sql_query(
                "SELECT COUNT(*) as count, AVG(area_hectare) as avg_area FROM land_records WHERE district LIKE '%Agra%'",
                conn
            )
            if not df.empty and df.iloc[0]['count'] > 0:
                count = df.iloc[0]['count']
                avg_area = df.iloc[0]['avg_area'] or 0
                print(f"🤖 आगरा में {count} भूमि रिकॉर्ड हैं, औसत क्षेत्रफल {avg_area:.2f} हेक्टेयर")
            else:
                print("🤖 आगरा के लिए कोई रिकॉर्ड नहीं मिला")

        elif any(word in user_input.lower() for word in ['mutation', 'म्यूटेशन']):
            df = pd.read_sql_query(
                "SELECT answer FROM legal_faqs WHERE tags LIKE '%mutation%' LIMIT 1",
                conn
            )
            if not df.empty:
                print(f"🤖 {df.iloc[0]['answer']}")
            else:
                print("🤖 म्यूटेशन की जानकारी: यह भूमि स्वामित्व बदलने की प्रक्रिया है")

        elif any(word in user_input.lower() for word in ['khasra', 'खसरा']):
            print("🤖 खसरा नंबर: भूमि के टुकड़े की विशिष्ट पहचान संख्या है। यह सरकारी रिकॉर्ड में जमीन की पहचान के लिए उपयोग होती है।")

        elif any(word in user_input.lower() for word in ['registry', 'रजिस्ट्री']):
            print("🤖 रजिस्ट्री के लिए आवश्यक दस्तावेज: बिक्री पत्र, पुराना रजिस्ट्री दस्तावेज, खसरा/खतौनी, आधार कार्ड, PAN कार्ड")

        elif any(word in user_input.lower() for word in ['help', 'मदद']):
            print("🤖 मैं निम्न विषयों में मदद कर सकता हूं:")
            print("   • भूमि रिकॉर्ड खोजना")
            print("   • म्यूटेशन प्रक्रिया")
            print("   • रजिस्ट्री की जानकारी")
            print("   • खसरा नंबर की व्याख्या")

        else:
            print("🤖 मैं आपकी भूमि संबंधी समस्या में मदद करने की कोशिश कर रहा हूं। कृपया अधिक स्पष्ट प्रश्न पूछें।")

    conn.close()
    print("👋 धन्यवाद!")

def main_menu():
    """Main menu for LandGPT"""
    print("🌾 LandGPT - AI Legal Assistant for Land Records")
    print("=" * 50)

    while True:
        print("\n📋 Main Menu:")
        print("1. 🚀 Quick Setup (Install + Database + Demo)")
        print("2. 🗄️ Setup Database Only")
        print("3. 🎬 Run Demo")
        print("4. 💬 Interactive Query")
        print("5. 📊 View Database Stats")
        print("6. 🚪 Exit")

        choice = input("\nSelect option (1-6): ").strip()

        if choice == '1':
            print("\n🚀 Running Quick Setup...")
            install_requirements()
            if check_files() and setup_database():
                run_demo()
                print("\n✅ Quick setup completed!")

        elif choice == '2':
            if check_files():
                setup_database()

        elif choice == '3':
            if os.path.exists("landgpt.db"):
                run_demo()
            else:
                print("❌ Database not found. Please run setup first.")

        elif choice == '4':
            if os.path.exists("landgpt.db"):
                interactive_query()
            else:
                print("❌ Database not found. Please run setup first.")

        elif choice == '5':
            if os.path.exists("landgpt.db"):
                show_database_stats()
            else:
                print("❌ Database not found. Please run setup first.")

        elif choice == '6':
            print("👋 Thank you for using LandGPT!")
            break

        else:
            print("❌ Invalid option. Please choose 1-6.")

def show_database_stats():
    """Show database statistics"""
    import sqlite3
    import pandas as pd

    print("\n📊 Database Statistics:")
    print("-" * 30)

    conn = sqlite3.connect("landgpt.db")

    # Count records
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM land_records")
    land_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM legal_faqs")
    faq_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT district) FROM land_records")
    district_count = cursor.fetchone()[0]

    print(f"📄 Land Records: {land_count}")
    print(f"❓ Legal FAQs: {faq_count}")
    print(f"🏙️ Districts: {district_count}")

    # Show sample records
    if land_count > 0:
        print(f"\n📝 Sample Records:")
        df = pd.read_sql_query("SELECT district, village, owner_name, khasra_number FROM land_records LIMIT 3", conn)
        for _, row in df.iterrows():
            print(f"   • {row['district']} - {row['village']} - Khasra {row['khasra_number']}")

    conn.close()

if __name__ == "__main__":
    main_menu()