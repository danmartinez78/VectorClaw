#!/usr/bin/env python3
"""VectorClaw Hardware Smoke Test - Direct SDK Test"""
import os
import sys
import json
import base64
from datetime import datetime
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test output directory
OUT_DIR = Path.home() / ".openclaw/workspace/VectorClaw/hardware_test_2026-02-28"
OUT_DIR.mkdir(exist_ok=True)

def save_image(image_b64: str, name: str) -> str:
    """Save base64 image to test directory"""
    img_data = base64.b64decode(image_b64)
    out_path = OUT_DIR / f"{name}.jpg"
    out_path.write_bytes(img_data)
    return str(out_path)

def run_test(name: str, test_fn) -> dict:
    """Run a test and return result"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    try:
        result = test_fn()
        result["test"] = name
        result["status"] = "ok"
        print(f"✅ PASS")
        print(f"Result: {json.dumps(result, indent=2, default=str)}")
        return result
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return {"test": name, "status": "error", "error": str(e)}

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     VectorClaw Hardware Smoke Test + Empirical Study      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"Time: {datetime.now()}")
    print(f"Output dir: {OUT_DIR}")
    
    # Import after path setup
    from vectorclaw_mcp import robot as robot_mod
    from anki_vector.util import distance_mm, speed_mmps, degrees
    
    results = []
    
    # ===========================================
    # PHASE 1: CORE TOOL VALIDATION
    # ===========================================
    
    # 1.1 Status
    def test_status():
        from vectorclaw_mcp.tools_perception import vector_status
        return vector_status()
    
    results.append(run_test("1.1 vector_status", test_status))
    
    # 1.2 Pose
    def test_pose():
        from vectorclaw_mcp.tools_perception import vector_pose
        return vector_pose()
    
    results.append(run_test("1.2 vector_pose", test_pose))
    
    # 5.1 Proximity (NEW FIELDS!)
    def test_proximity():
        from vectorclaw_mcp.tools_perception import vector_proximity_status
        return vector_proximity_status()
    
    results.append(run_test("5.1 vector_proximity_status", test_proximity))
    
    # 4.1 Camera capture
    def test_look():
        from vectorclaw_mcp.tools_perception import vector_capture_image
        result = vector_capture_image()
        if result.get("image_base64"):
            path = save_image(result["image_base64"], f"capture_{datetime.now().strftime('%H%M%S')}")
            result["image_saved_to"] = path
            del result["image_base64"]  # Don't print huge base64
        return result
    
    results.append(run_test("4.1 vector_capture_image", test_look))
    
    # 3.1 Speech
    def test_say():
        from vectorclaw_mcp.tools_motion import vector_say
        return vector_say("Hardware smoke test")
    
    results.append(run_test("3.1 vector_say", test_say))
    
    # ===========================================
    # SUMMARY
    # ===========================================
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results if r.get("status") == "ok")
    failed = sum(1 for r in results if r.get("status") == "error")
    
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    for r in results:
        status = "✅" if r.get("status") == "ok" else "❌"
        print(f"  {status} {r['test']}")
    
    # Save results
    results_path = OUT_DIR / "test_results.json"
    results_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nResults saved to: {results_path}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
