import os
import traceback
import sqlite3

def run():
    db_name = "test_mem_standalone.db"
    if os.path.exists(db_name): os.remove(db_name)
    try:
        from aurora.memory.session_db import MemoryManager
        mem = MemoryManager(db_name)
        uid = mem.create_or_update_session(None, {"name": "Test Project"})
        mem.save_section(uid, "market_analysis", "Mock Content")
        data = mem.load_session(uid)
        
        if data["sections"]["market_analysis"] != "Mock Content": 
            raise ValueError("Memory mismatch")
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        return False
    finally:
        # Give Windows a moment to release file handles before deleting
        try:
            import time; time.sleep(0.5)
            if os.path.exists(db_name): os.remove(db_name)
        except Exception as cleanup_e:
            print(f"Cleanup warning: {cleanup_e}")
            
    print("Memory DB Test: PASSED")
    return True

run()
