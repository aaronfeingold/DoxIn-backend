#!/usr/bin/env python3
"""
Neon Database Verification Script
Checks connection, schema, and functionality
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()


def test_connection():
    """Test basic database connection"""
    print("🔌 Testing database connection...")

    neon_url = os.environ.get('NEON_DATABASE_URL') or os.environ.get('DATABASE_URL')

    if not neon_url:
        print("❌ No database URL found in environment")
        return False

    # Mask password in URL for display
    display_url = neon_url
    if '@' in display_url:
        parts = display_url.split('@')
        if ':' in parts[0]:
            user_pass = parts[0].split('://')[-1]
            if ':' in user_pass:
                user = user_pass.split(':')[0]
                display_url = display_url.replace(user_pass, f"{user}:***")

    print(f"📡 Connecting to: {display_url}")

    try:
        conn = psycopg2.connect(neon_url)
        cursor = conn.cursor()

        # Test basic query
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]

        # Get connection info
        cursor.execute("""
            SELECT
                current_database() as database,
                current_user as user,
                inet_server_addr() as server_addr,
                inet_server_port() as server_port
        """)
        conn_info = cursor.fetchone()

        cursor.close()
        conn.close()

        print("✅ Connection successful!")
        print(f"   Database: {conn_info[0]}")
        print(f"   User: {conn_info[1]}")
        print(f"   Server: {conn_info[2]}:{conn_info[3]}")
        print(f"   Version: {version.split(',')[0]}")

        return True

    except psycopg2.Error as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_extensions():
    """Test required PostgreSQL extensions"""
    print("\n🧩 Testing PostgreSQL extensions...")

    neon_url = os.environ.get('NEON_DATABASE_URL') or os.environ.get('DATABASE_URL')

    try:
        conn = psycopg2.connect(neon_url)
        cursor = conn.cursor()

        # Check for required extensions
        extensions = ['vector', 'uuid-ossp']

        for ext in extensions:
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM pg_extension WHERE extname = %s
                )
            """, (ext,))

            exists = cursor.fetchone()[0]
            if exists:
                print(f"✅ {ext}: Available")
            else:
                print(f"❌ {ext}: Not found")

        # Test vector operations
        print("\n🧮 Testing vector operations...")
        try:
            cursor.execute("SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector as distance")
            distance = cursor.fetchone()[0]
            print(f"✅ Vector distance calculation: {distance}")

            cursor.execute("SELECT '[1,0,0]'::vector <=> '[0,1,0]'::vector as cosine_distance")
            cosine_dist = cursor.fetchone()[0]
            print(f"✅ Cosine distance calculation: {cosine_dist}")

        except Exception as e:
            print(f"❌ Vector operations failed: {e}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Extension test failed: {e}")
        return False


def test_schema():
    """Test database schema and tables"""
    print("\n📊 Testing database schema...")

    neon_url = os.environ.get('NEON_DATABASE_URL') or os.environ.get('DATABASE_URL')

    try:
        conn = psycopg2.connect(neon_url)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("""
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        tables = cursor.fetchall()

        if not tables:
            print("⚠️  No tables found in public schema")
            print("   Run 'python scripts/migrate_to_neon.py' to apply schema")
            return False

        print(f"✅ Found {len(tables)} tables:")
        for table_name, table_type in tables:
            print(f"   📋 {table_name} ({table_type})")

        # Test specific tables that should exist
        expected_tables = ['users', 'invoices', 'companies', 'processing_jobs']
        missing_tables = []

        for table in expected_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name = %s
                )
            """, (table,))

            exists = cursor.fetchone()[0]
            if exists:
                print(f"✅ Core table '{table}': Present")
            else:
                print(f"❌ Core table '{table}': Missing")
                missing_tables.append(table)

        if missing_tables:
            print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
            print("   Schema may be incomplete or not applied")

        cursor.close()
        conn.close()
        return len(missing_tables) == 0

    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False


def test_performance():
    """Test basic database performance"""
    print("\n⚡ Testing database performance...")

    neon_url = os.environ.get('NEON_DATABASE_URL') or os.environ.get('DATABASE_URL')

    try:
        conn = psycopg2.connect(neon_url)
        cursor = conn.cursor()

        import time

        # Test simple query performance
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables")
        result = cursor.fetchone()[0]
        query_time = (time.time() - start_time) * 1000

        print(f"✅ Simple query: {query_time:.2f}ms ({result} tables)")

        # Test connection pool settings
        cursor.execute("SHOW max_connections")
        max_conn = cursor.fetchone()[0]
        print(f"✅ Max connections: {max_conn}")

        # Check current connections
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_stat_activity
            WHERE state = 'active'
        """)
        active_conn = cursor.fetchone()[0]
        print(f"✅ Active connections: {active_conn}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def test_flask_integration():
    """Test Flask app database integration"""
    print("\n🌶️  Testing Flask integration...")

    try:
        # Try to import and configure Flask app
        from app import create_app, db

        app = create_app()
        with app.app_context():
            # Test SQLAlchemy connection
            result = db.session.execute(db.text('SELECT 1 as test')).fetchone()
            if result and result[0] == 1:
                print("✅ SQLAlchemy connection: Working")
            else:
                print("❌ SQLAlchemy connection: Failed")

            # Check if models can be imported
            try:
                from app.models import Invoice, Company, User
                print("✅ Model imports: Working")
            except ImportError as e:
                print(f"❌ Model imports failed: {e}")

            # Test database URL detection
            db_url = str(db.engine.url)
            if 'neon.tech' in db_url:
                print("✅ Neon database detected")
            else:
                print("⚠️  Not using Neon database")

        return True

    except ImportError:
        print("⚠️  Flask app not available (run from backend/api directory)")
        return None
    except Exception as e:
        print(f"❌ Flask integration test failed: {e}")
        return False


def main():
    """Main verification process"""
    print("=" * 60)
    print("🔍 NEON DATABASE VERIFICATION")
    print("=" * 60)

    tests = [
        ("Connection", test_connection),
        ("Extensions", test_extensions),
        ("Schema", test_schema),
        ("Performance", test_performance),
        ("Flask Integration", test_flask_integration),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "="*60)
    print("📋 VERIFICATION SUMMARY")
    print("="*60)

    passed = 0
    failed = 0
    skipped = 0

    for test_name, result in results:
        if result is True:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        elif result is False:
            print(f"❌ {test_name}: FAILED")
            failed += 1
        else:
            print(f"⚠️  {test_name}: SKIPPED")
            skipped += 1

    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")

    if failed == 0:
        print("\n🎉 All tests passed! Your Neon database is ready.")
    else:
        print(f"\n💥 {failed} test(s) failed. Check the issues above.")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)