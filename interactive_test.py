import json
import sys
import requests

def main(filepath):
    # Stats
    total_processed = 0
    correct_detection = 0
    incorrect_detection = 0
    correct_no_idiom = 0
    incorrect_no_idiom = 0
    definition_approved = 0
    definition_rejected = 0
    definition_not_quite = 0

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # We assume a JSONL format (one JSON object per line)
            # {"idiom": "", "sent": ""}
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Could not find file {filepath}")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return

    print(f"Loaded {len(lines)} examples. Starting interactive testing...\n")
    print("Press Ctrl+C at any time to stop and view your current stats.")
    print("-" * 50)

    try:
        for line in lines:
            data = json.loads(line)
            expected_idiom = data.get("idiom")
            sentence = data.get("sent", "")

            if not sentence:
                continue

            total_processed += 1
            print(f"\n[Example {total_processed}/{len(lines)}]")
            print(f"Sentence: {sentence}")
            print(f"Expected Idiom: {expected_idiom if expected_idiom else 'None'}")
            
            # Call application backend
            try:
                response = requests.post("http://localhost:8000/detect", json={"text": sentence})
                response.raise_for_status()
                result = response.json()
            except Exception as e:
                print(f"Error connecting to backend: {e}")
                print("Make sure your backend is running at http://localhost:8000")
                return

            detected_idioms = [item["idiom"] for item in result.get("idioms", [])]
            detected_data = {item["idiom"]: item for item in result.get("idioms", [])}
            
            # 1. Check if the application correctly detected the expected idiom (or lack thereof)
            if expected_idiom:
                if expected_idiom in detected_idioms:
                    print(f"✅ Detection Success: Found expected idiom '{expected_idiom}'.")
                    correct_detection += 1
                    
                    # 2. Prompt for definition accuracy check
                    meta = detected_data[expected_idiom]
                    print(f"\nApp Definition (EN): {meta.get('meaning_en')}")
                    if meta.get('alternative_meanings_en'):
                        print(f"Alt Meanings (EN): {', '.join(meta.get('alternative_meanings_en'))}")
                    
                    while True:
                        user_input = input("\nDoes this definition match your understanding? (y/n/u/skip): ").strip().lower()
                        if user_input in ['y', 'yes']:
                            definition_approved += 1
                            print("✅ Definition approved.")
                            break
                        elif user_input in ['n', 'no']:
                            definition_rejected += 1
                            print("❌ Definition rejected.")
                            break
                        elif user_input in ['u', 'unsatisfactory']:
                            definition_not_quite += 1
                            print("⚠️ Definition somewhat right, but unsatisfactory.")
                            break
                        elif user_input in ['s', 'skip']:
                            print("⚠️ Definition skipped.")
                            break
                        else:
                            print("Please enter 'y', 'n', 'u', or 'skip'.")
                else:
                    print(f"❌ Detection Failure: Expected '{expected_idiom}', but detected {detected_idioms if detected_idioms else 'nothing'}.")
                    incorrect_detection += 1
            else:
                # Case where expected_idiom is null or empty
                if not detected_idioms:
                    print("✅ Success: Correctly identified no idioms.")
                    correct_no_idiom += 1
                else:
                    print(f"❌ False Positive: Expected no idiom, but detected {detected_idioms}.")
                    incorrect_no_idiom += 1

            print("-" * 50)
            
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user.")

    # Print final live-counter stats
    print("\n" + "=" * 50)
    print("FINAL STATISTICS")
    print("=" * 50)
    print(f"Total Sentences Processed: {total_processed}")
    print(f"Correctly Detected Idioms: {correct_detection}")
    print(f"Missed/Incorrect Idioms: {incorrect_detection}")
    print(f"Correctly Identified No Idiom: {correct_no_idiom}")
    print(f"False Positives (Found idiom when expected none): {incorrect_no_idiom}")
    print("-" * 50)
    
    total_evaluated = definition_approved + definition_rejected + definition_not_quite
    if total_evaluated > 0:
        accuracy = (definition_approved / total_evaluated) * 100
        not_quite_accuracy = (definition_approved + definition_not_quite) / total_evaluated * 100
        print(f"User Approved Definitions: {definition_approved}")
        print(f"User Rejected Definitions: {definition_rejected}")
        print(f"User Somewhat Right Definitions: {definition_not_quite}")
        print(f"Definition Accuracy: {accuracy:.2f}%")
        print(f"Definition Accuracy (including somewhat right): {not_quite_accuracy:.2f}%")
    else:
        print("No definitions were evaluated.")
    print("=" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python interactive_test.py <path_to_jsonl_file>")
    else:
        main(sys.argv[1])
