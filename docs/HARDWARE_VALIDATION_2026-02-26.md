# Hardware Validation Report (2026-02-26)

## Scope
Initial on-robot validation for VectorClaw using a real Vector robot on Wire-Pod.

- Host: `section9`
- Robot: `Vector-S9R3` (`00a1546c`)
- Network: local WiFi via Wire-Pod

## Test Method
Command-by-command protocol:
1. Send one command
2. Observe robot behavior
3. Human verifies outcome before next command

This was necessary because Vector idle behavior can be mistaken for commanded motion.

## Verified Results

### Core motion and control
- ✅ `vector_drive_off_charger`: visually confirmed off-charger behavior
- ✅ `vector_drive` forward: visually confirmed
- ✅ `vector_drive` reverse: visually confirmed
- ✅ `vector_drive` left turn (90°): visually confirmed

### Sensing and state
- ✅ `vector_status`: valid state payload returned
- ✅ `vector_pose`: valid pose payload returned
- ✅ `vector_look`: image payload returned

### Interaction
- ✅ `vector_say`: audible speech confirmed

### Environment-dependent / pending deeper validation
- ⚠️ `vector_face`: requires robust valid-image test vectors and shape constraints
- ⚠️ `vector_cube`: requires cube paired/available
- ⚠️ `vector_animate`: depends on animation-list behavior in current SDK/Wire-Pod path

## Observed Limitation
Idle/ambient robot behavior remains active and can confound visual verification.

**Mitigation that worked:** large discrete movements + explicit human confirmation after each command.

## Outcome
Initial hardware validation is considered a **success** for core command, motion, sensing, and speech pathways.
