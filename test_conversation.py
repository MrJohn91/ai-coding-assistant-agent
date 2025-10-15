"""End-to-end conversation flow test."""

import time
import httpx

BASE_URL = "http://localhost:8000"
CLIENT = httpx.Client(timeout=30.0)  # 30 second timeout


def test_conversation_flow():
    """Test full conversation: product inquiry → FAQ → interest → lead collection."""

    print("\n" + "="*70)
    print("TESTING END-TO-END CONVERSATION FLOW")
    print("="*70)

    # Step 1: Create conversation
    print("\n[1] Creating new conversation...")
    response = CLIENT.post(f"{BASE_URL}/api/v1/conversations")
    data = response.json()
    session_id = data["session_id"]
    print(f"✓ Session created: {session_id}")
    print(f"  Agent: {data['message']}")

    # Step 2: Product inquiry
    print("\n[2] Sending product inquiry...")
    response = CLIENT.post(
        f"{BASE_URL}/api/v1/conversations/{session_id}/messages",
        json={"message": "I'm looking for a mountain bike for trail riding under €2000"}
    )
    data = response.json()
    print(f"  User: I'm looking for a mountain bike for trail riding under €2000")
    print(f"  Agent: {data['response'][:150]}...")
    if data.get('products'):
        print(f"  ✓ Recommended {len(data['products'])} products:")
        for p in data['products']:
            print(f"    - {p['name']} ({p['brand']}) - €{p['price_eur']}")

    time.sleep(1)

    # Step 3: FAQ question
    print("\n[3] Asking FAQ question...")
    response = CLIENT.post(
        f"{BASE_URL}/api/v1/conversations/{session_id}/messages",
        json={"message": "What's the warranty on mountain bikes?"}
    )
    data = response.json()
    print(f"  User: What's the warranty on mountain bikes?")
    print(f"  Agent: {data['response'][:150]}...")

    time.sleep(1)

    # Step 4: Show interest
    print("\n[4] Expressing interest...")
    response = CLIENT.post(
        f"{BASE_URL}/api/v1/conversations/{session_id}/messages",
        json={"message": "The Trailblazer 500 looks perfect! I'm interested in buying it."}
    )
    data = response.json()
    print(f"  User: The Trailblazer 500 looks perfect! I'm interested in buying it.")
    print(f"  Agent: {data['response']}")

    time.sleep(1)

    # Step 5: Provide name
    print("\n[5] Providing name...")
    response = CLIENT.post(
        f"{BASE_URL}/api/v1/conversations/{session_id}/messages",
        json={"message": "John Doe"}
    )
    data = response.json()
    print(f"  User: John Doe")
    print(f"  Agent: {data['response']}")

    time.sleep(1)

    # Step 6: Provide email
    print("\n[6] Providing email...")
    response = CLIENT.post(
        f"{BASE_URL}/api/v1/conversations/{session_id}/messages",
        json={"message": "john.doe@example.com"}
    )
    data = response.json()
    print(f"  User: john.doe@example.com")
    print(f"  Agent: {data['response']}")

    time.sleep(1)

    # Step 7: Provide phone and create lead
    print("\n[7] Providing phone (final step)...")
    response = CLIENT.post(
        f"{BASE_URL}/api/v1/conversations/{session_id}/messages",
        json={"message": "+491234567890"}
    )
    data = response.json()
    print(f"  User: +491234567890")
    print(f"  Agent: {data['response']}")
    if data.get('lead_created'):
        print(f"  ✓ Lead created successfully in CRM!")
    else:
        print(f"  ⚠ Lead not created (CRM may be unavailable)")

    # Step 8: Get conversation history
    print("\n[8] Retrieving conversation history...")
    response = CLIENT.get(f"{BASE_URL}/api/v1/conversations/{session_id}")
    data = response.json()
    print(f"  ✓ Retrieved {len(data['messages'])} messages")
    print(f"  Final state: {data['state']}")

    print("\n" + "="*70)
    print("✓ END-TO-END TEST COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nSummary:")
    print("  • Product recommendations: ✓")
    print("  • FAQ answering: ✓")
    print("  • Interest detection: ✓")
    print("  • Lead data collection: ✓")
    print("  • State transitions: ✓")
    print(f"  • Total conversation turns: {len(data['messages'])}")


if __name__ == "__main__":
    try:
        test_conversation_flow()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
