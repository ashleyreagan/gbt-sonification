#!/usr/bin/env python3
"""
Example customization script for GBT sonification.
Shows different ways to generate sounds for different moods.
"""

from gbt_sonification import GBTSonifier

def create_deep_space_ambient():
    """
    Create long, deep ambient pieces (10 minutes each).
    Perfect for meditation or background ambience.
    """
    print("\n🌌 Creating Deep Space Ambient Collection...")
    sonifier = GBTSonifier(output_dir="deep_space_ambient")
    
    files = sonifier.create_ambient_pieces(
        num_pieces=3,
        duration_minutes=10  # Longer pieces
    )
    
    return files


def create_lofi_elements():
    """
    Create shorter pieces optimized for lofi production.
    Great for chopping, sampling, and layering.
    """
    print("\n🎹 Creating Lofi Elements Collection...")
    sonifier = GBTSonifier(output_dir="lofi_elements")
    
    files = sonifier.create_ambient_pieces(
        num_pieces=5,  # More variety
        duration_minutes=3  # Shorter, more focused
    )
    
    return files


def create_sample_pack():
    """
    Create a variety pack with different lengths.
    """
    print("\n📦 Creating Sample Pack...")
    
    all_files = []
    
    # Short textures (1 minute)
    print("\n--- Creating short textures ---")
    sonifier1 = GBTSonifier(output_dir="sample_pack/textures")
    files1 = sonifier1.create_ambient_pieces(num_pieces=3, duration_minutes=1)
    all_files.extend(files1)
    
    # Medium pads (3 minutes)
    print("\n--- Creating medium pads ---")
    sonifier2 = GBTSonifier(output_dir="sample_pack/pads")
    files2 = sonifier2.create_ambient_pieces(num_pieces=3, duration_minutes=3)
    all_files.extend(files2)
    
    # Long drones (7 minutes)
    print("\n--- Creating long drones ---")
    sonifier3 = GBTSonifier(output_dir="sample_pack/drones")
    files3 = sonifier3.create_ambient_pieces(num_pieces=2, duration_minutes=7)
    all_files.extend(files3)
    
    print(f"\n✓ Sample pack complete! {len(all_files)} files created.")
    return all_files


def create_quick_batch():
    """
    Quickly generate several short pieces for immediate use.
    """
    print("\n⚡ Quick Batch Generation...")
    sonifier = GBTSonifier(output_dir="quick_batch")
    
    files = sonifier.create_ambient_pieces(
        num_pieces=10,  # Lots of variety
        duration_minutes=2  # Quick 2-minute pieces
    )
    
    return files


def main():
    """
    Menu for different generation modes.
    """
    print("=" * 70)
    print("GBT SONIFICATION - CUSTOM GENERATION MODES")
    print("=" * 70)
    print("\nChoose a mode:")
    print("1. Deep Space Ambient (3 x 10-minute pieces)")
    print("2. Lofi Elements (5 x 3-minute pieces)")
    print("3. Sample Pack (variety of lengths)")
    print("4. Quick Batch (10 x 2-minute pieces)")
    print("5. All of the above!")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        create_deep_space_ambient()
    elif choice == "2":
        create_lofi_elements()
    elif choice == "3":
        create_sample_pack()
    elif choice == "4":
        create_quick_batch()
    elif choice == "5":
        print("\n🚀 Generating everything! This will take a few minutes...\n")
        create_deep_space_ambient()
        create_lofi_elements()
        create_sample_pack()
        create_quick_batch()
        print("\n🎉 All collections created successfully!")
    else:
        print("\nInvalid choice. Running default (Lofi Elements)...")
        create_lofi_elements()
    
    print("\n✨ Done! Check your output folders for the audio files.")


if __name__ == "__main__":
    main()
