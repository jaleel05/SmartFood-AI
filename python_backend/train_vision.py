import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms, datasets
from PIL import Image
import json
import time
import numpy as np
from tqdm import tqdm
import random
from sklearn.model_selection import train_test_split

# ==================== CONFIGURATION ====================
FRUITS_PATH = r'D:\AI\Dataset\Fruits'
VEGETABLES_PATH = r'D:\AI\Dataset\Vegetable'
NUM_EPOCHS = 817  # 817 epochs full training
BATCH_SIZE = 32
IMG_SIZE = 224
LEARNING_RATE = 0.001
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print("="*80)
print("FOOD FRESHNESS CLASSIFICATION - COMPLETE TRAINING")
print(f"Device: {DEVICE}")
print(f"Epochs: {NUM_EPOCHS}")
print("="*80)

# ==================== DATASET FUNCTIONS ====================
def scan_dataset():
    """Scan all classes and images"""
    print("\n📂 Scanning dataset structure...")
    
    all_classes = []
    class_images = {}
    total_images = 0
    
    # Scan Fruits folder
    if os.path.exists(FRUITS_PATH):
        for class_name in os.listdir(FRUITS_PATH):
            class_path = os.path.join(FRUITS_PATH, class_name)
            if os.path.isdir(class_path):
                images = [f for f in os.listdir(class_path) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))]
                if images:
                    all_classes.append(class_name)
                    class_images[class_name] = images
                    total_images += len(images)
                    print(f"  ✓ Fruits/{class_name}: {len(images)} images")
    
    # Scan Vegetables folder
    if os.path.exists(VEGETABLES_PATH):
        for class_name in os.listdir(VEGETABLES_PATH):
            class_path = os.path.join(VEGETABLES_PATH, class_name)
            if os.path.isdir(class_path):
                images = [f for f in os.listdir(class_path) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))]
                if images:
                    all_classes.append(class_name)
                    class_images[class_name] = images
                    total_images += len(images)
                    print(f"  ✓ Vegetables/{class_name}: {len(images)} images")
    
    if not all_classes:
        print("❌ No classes found! Creating sample structure...")
        # Create sample directories for testing
        sample_classes = ['fresh_apple', 'stale_apple', 'fresh_banana', 'stale_banana']
        return sample_classes, {'fresh_apple': [], 'stale_apple': [], 'fresh_banana': [], 'stale_banana': []}, 0
    
    print(f"\n📊 Dataset Summary:")
    print(f"  • Total Classes: {len(all_classes)}")
    print(f"  • Total Images: {total_images}")
    print(f"  • Average per class: {total_images//len(all_classes) if all_classes else 0}")
    
    return sorted(all_classes), class_images, total_images

class FoodDataset(Dataset):
    """Custom Dataset for Food Images"""
    def __init__(self, classes, class_images, transform=None, mode='train'):
        self.classes = classes
        self.class_to_idx = {cls: idx for idx, cls in enumerate(classes)}
        self.transform = transform
        self.mode = mode
        
        self.image_paths = []
        self.labels = []
        
        print(f"\n📥 Loading {mode} dataset...")
        
        for class_name in classes:
            images = class_images.get(class_name, [])
            if not images:
                continue
                
            # Determine which folder
            fruit_path = os.path.join(FRUITS_PATH, class_name)
            veg_path = os.path.join(VEGETABLES_PATH, class_name)
            
            if os.path.exists(fruit_path):
                base_path = fruit_path
            elif os.path.exists(veg_path):
                base_path = veg_path
            else:
                continue
            
            # Split for train/val
            random.shuffle(images)
            split_idx = int(len(images) * 0.8)  # 80% train, 20% val
            
            if mode == 'train':
                selected_images = images[:split_idx]
            else:  # val
                selected_images = images[split_idx:]
            
            for img_name in selected_images:
                img_path = os.path.join(base_path, img_name)
                if os.path.exists(img_path):
                    self.image_paths.append(img_path)
                    self.labels.append(self.class_to_idx[class_name])
            
            print(f"  • {class_name}: {len(selected_images)} images")
        
        print(f"  ✅ Total {mode} images: {len(self.image_paths)}")
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        try:
            img = Image.open(self.image_paths[idx]).convert('RGB')
            label = self.labels[idx]
            
            if self.transform:
                img = self.transform(img)
            
            return img, label
        except Exception as e:
            # Return a dummy image if error
            print(f"Error loading {self.image_paths[idx]}: {e}")
            dummy_img = torch.zeros(3, IMG_SIZE, IMG_SIZE)
            return dummy_img, 0

# ==================== MODEL FUNCTIONS ====================
def create_model(num_classes):
    """Create and initialize model"""
    print(f"\n🤖 Creating model for {num_classes} classes...")
    
    # Use ResNet50 for better accuracy
    model = models.resnet50(pretrained=True)
    
    # Freeze early layers
    for param in model.parameters():
        param.requires_grad = False
    
    # Unfreeze last few layers
    for param in model.layer4.parameters():
        param.requires_grad = True
    
    # Modify final layer
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_features, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )
    
    return model

def get_transforms():
    """Create data transforms"""
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    
    return train_transform, val_transform

# ==================== TRAINING FUNCTIONS ====================
def train_one_epoch(model, train_loader, criterion, optimizer, epoch, num_epochs):
    """Train for one epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs} [Train]')
    for batch_idx, (inputs, targets) in enumerate(pbar):
        inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()
        
        # Update progress bar
        pbar.set_postfix({
            'Loss': f'{running_loss/(batch_idx+1):.4f}',
            'Acc': f'{100.*correct/total:.2f}%'
        })
    
    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100. * correct / total
    
    return epoch_loss, epoch_acc

def validate(model, val_loader, criterion):
    """Validate model"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        pbar = tqdm(val_loader, desc='[Validation]')
        for batch_idx, (inputs, targets) in enumerate(pbar):
            inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)
            
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            running_loss += loss.item()
            
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            pbar.set_postfix({
                'Acc': f'{100.*correct/total:.2f}%'
            })
    
    val_loss = running_loss / len(val_loader)
    val_acc = 100. * correct / total
    
    return val_loss, val_acc

# ==================== MAIN TRAINING FUNCTION ====================
def main_training():
    """Main training loop"""
    print("\n" + "="*80)
    print("🚀 STARTING TRAINING")
    print("="*80)
    
    # Step 1: Scan dataset
    classes, class_images, total_images = scan_dataset()
    
    if total_images == 0:
        print(" No images found! Please check your dataset paths.")
        print(f"   Fruits Path: {FRUITS_PATH}")
        print(f"   Vegetables Path: {VEGETABLES_PATH}")
        return False
    
    # Step 2: Create transforms
    train_transform, val_transform = get_transforms()
    
    # Step 3: Create datasets
    train_dataset = FoodDataset(classes, class_images, train_transform, 'train')
    val_dataset = FoodDataset(classes, class_images, val_transform, 'val')
    
    if len(train_dataset) == 0 or len(val_dataset) == 0:
        print(" Not enough images for training/validation!")
        return False
    
    # Step 4: Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=2,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=2,
        pin_memory=True
    )
    
    print(f"\n Data Loaders Ready:")
    print(f"  • Training batches: {len(train_loader)}")
    print(f"  • Validation batches: {len(val_loader)}")
    print(f"  • Classes: {len(classes)}")
    
    # Step 5: Create model
    model = create_model(len(classes))
    model = model.to(DEVICE)
    
    # Step 6: Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=10
    )
    
    # Step 7: Training variables
    best_acc = 0.0
    train_losses = []
    val_accuracies = []
    
    start_time = time.time()
    
    print("\n" + "="*80)
    print("🔥 TRAINING PROGRESS")
    print("="*80)
    
    # Step 8: Training loop
    for epoch in range(NUM_EPOCHS):
        epoch_start = time.time()
        
        # Train
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, epoch, NUM_EPOCHS
        )
        train_losses.append(train_loss)
        
        # Validate
        val_loss, val_acc = validate(model, val_loader, criterion)
        val_accuracies.append(val_acc)
        
        # Update learning rate
        scheduler.step(val_acc)
        
        epoch_time = time.time() - epoch_start
        
        # Print epoch summary
        print(f"\n Epoch {epoch+1}/{NUM_EPOCHS} Summary:")
        print(f"    Time: {epoch_time:.1f}s")
        print(f"    Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"    Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        print(f"    Best Acc: {best_acc:.2f}%")
        print(f"    Learning Rate: {optimizer.param_groups[0]['lr']:.6f}")
        
        # Save best model
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'classes': classes,
                'class_to_idx': train_dataset.class_to_idx,
                'train_loss': train_loss,
                'val_accuracy': val_acc,
                'best_accuracy': best_acc,
            }, 'food_model_best.pth')
            print(f"    Saved best model (Accuracy: {val_acc:.2f}%)")
        
        # Save checkpoint every 100 epochs
        if (epoch + 1) % 100 == 0:
            checkpoint_path = f'checkpoint_epoch_{epoch+1}.pth'
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'val_accuracy': val_acc,
            }, checkpoint_path)
            print(f"    Saved checkpoint: {checkpoint_path}")
        
        # Early stopping check
        if epoch > 100:
            recent_acc = val_accuracies[-20:]
            if max(recent_acc) - min(recent_acc) < 2.0:
                print(f"\n  Early stopping: Accuracy plateau detected")
                break
    
    total_time = time.time() - start_time
    
    # ==================== SAVE RESULTS ====================
    print("\n" + "="*80)
    print(" TRAINING COMPLETED")
    print("="*80)
    print(f" Total Time: {total_time/60:.1f} minutes")
    print(f" Best Accuracy: {best_acc:.2f}%")
    print(f" Final Accuracy: {val_accuracies[-1]:.2f}%")
    print(f" Epochs Trained: {len(train_losses)}")
    
    # Save final model
    torch.save({
        'model_state_dict': model.state_dict(),
        'classes': classes,
        'class_to_idx': train_dataset.class_to_idx,
        'train_losses': train_losses,
        'val_accuracies': val_accuracies,
        'best_accuracy': best_acc,
        'total_time_minutes': total_time/60
    }, 'food_model_final.pth')
    
    # Save class mapping
    class_info = {
        'classes': classes,
        'class_to_idx': train_dataset.class_to_idx,
        'idx_to_class': {idx: cls for idx, cls in enumerate(classes)},
        'num_classes': len(classes),
        'total_images': total_images,
        'train_images': len(train_dataset),
        'val_images': len(val_dataset),
        'best_accuracy': best_acc,
        'training_time': f'{total_time/60:.1f} minutes'
    }
    
    with open('class_mapping.json', 'w') as f:
        json.dump(class_info, f, indent=2)
    
    # Create food knowledge base
    print("\n Creating Food Knowledge Base...")
    food_kb = []
    calories_db = {
        'apple': '52', 'banana': '89', 'orange': '47', 'mango': '60',
        'tomato': '18', 'potato': '77', 'carrot': '41', 'broccoli': '34',
        'cabbage': '25', 'spinach': '23', 'cucumber': '15', 'onion': '40',
        'garlic': '149', 'ginger': '80', 'lemon': '29', 'pineapple': '50',
        'strawberry': '32', 'watermelon': '30', 'grapes': '69', 'pear': '57',
        'papaya': '43', 'pomegranate': '83', 'kiwi': '61', 'guava': '68'
    }
    
    for cls in classes:
        if '_' in cls:
            try:
                condition, food = cls.split('_')
            except:
                condition = 'unknown'
                food = cls
            
            calories = calories_db.get(food, '100')
            
            fruits = ['apple', 'banana', 'orange', 'mango', 'pineapple', 'watermelon',
                     'grapes', 'strawberry', 'peach', 'pear', 'plum', 'lemon',
                     'kiwi', 'papaya', 'pomegranate', 'guava', 'lychee', 'cherry']
            
            category = 'Fruit' if food in fruits else 'Vegetable'
            
            if condition == 'fresh':
                shelf_life = '7-10 days' if category == 'Fruit' else '5-7 days'
            elif condition == 'stale':
                shelf_life = '2-3 days' if category == 'Fruit' else '3-4 days'
            elif condition == 'rotten':
                shelf_life = 'Immediate disposal'
            else:
                shelf_life = '3-5 days'
            
            food_kb.append({
                'name': food.capitalize(),
                'original_class': cls,
                'condition': condition.capitalize(),
                'calories': calories,
                'shelfLife': shelf_life,
                'category': category
            })
    
    with open('food_knowledge_base.json', 'w') as f:
        json.dump(food_kb, f, indent=2)
    
    # Save training report
    report = {
        'training_summary': {
            'total_epochs': len(train_losses),
            'best_accuracy': best_acc,
            'final_accuracy': val_accuracies[-1],
            'training_time_minutes': total_time/60,
            'device': str(DEVICE),
            'batch_size': BATCH_SIZE,
            'learning_rate': LEARNING_RATE
        },
        'dataset_info': {
            'total_classes': len(classes),
            'total_images': total_images,
            'train_images': len(train_dataset),
            'val_images': len(val_dataset),
            'classes': classes
        }
    }
    
    with open('training_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # ==================== FINAL MESSAGE ====================
    print("\n" + "="*80)
    print(" ALL FILES CREATED SUCCESSFULLY!")
    print("="*80)
    print("\n📁 Created Files:")
    print("   1. food_model_best.pth    - Best trained model")
    print("   2. food_model_final.pth   - Final trained model")
    print("   3. class_mapping.json     - Class information")
    print("   4. food_knowledge_base.json - Food details")
    print("   5. training_report.json   - Training statistics")
    
    if best_acc > 80:
        print(f"\n EXCELLENT! Model achieved {best_acc:.2f}% accuracy!")
    elif best_acc > 70:
        print(f"\n GOOD! Model achieved {best_acc:.2f}% accuracy")
    elif best_acc > 60:
        print(f"\n  AVERAGE! Model achieved {best_acc:.2f}% accuracy")
    else:
        print(f"\n NEEDS IMPROVEMENT! Model only achieved {best_acc:.2f}% accuracy")
        print("   Consider adding more training images")
    
    print("\n🚀 Now run your backend:")
    print("   python simple_backend.py")
    print("\n📱 Your frontend will now work with the trained model!")
    
    return True

# ==================== QUICK TRAINING OPTION ====================
def quick_training():
    """Quick training for testing"""
    print("\n⚡ QUICK TRAINING (10 epochs only)")
    
    # Same as main but with 10 epochs
    classes, class_images, total_images = scan_dataset()
    
    if total_images == 0:
        print("No images found!")
        return False
    
    train_transform, val_transform = get_transforms()
    train_dataset = FoodDataset(classes, class_images, train_transform, 'train')
    val_dataset = FoodDataset(classes, class_images, val_transform, 'val')
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    
    model = models.resnet18(pretrained=True)
    model.fc = nn.Linear(model.fc.in_features, len(classes))
    model = model.to(DEVICE)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    best_acc = 0
    print("\nTraining for 10 epochs...")
    
    for epoch in range(10):
        # Train
        model.train()
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
        
        # Validate
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)
                outputs = model(inputs)
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
        
        acc = 100. * correct / total
        print(f"Epoch {epoch+1}/10 - Acc: {acc:.2f}%")
        
        if acc > best_acc:
            best_acc = acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'classes': classes,
                'class_to_idx': train_dataset.class_to_idx,
                'accuracy': acc
            }, 'food_model_best.pth')
    
    print(f"\nQuick training complete! Best accuracy: {best_acc:.2f}%")
    
    # Save minimal files
    class_info = {
        'classes': classes,
        'class_to_idx': train_dataset.class_to_idx,
        'num_classes': len(classes)
    }
    with open('class_mapping.json', 'w') as f:
        json.dump(class_info, f, indent=2)
    
    print("Files created. Now run: python simple_backend.py")
    return True

# ==================== MAIN ENTRY POINT ====================
if __name__ == "__main__":
    print("="*80)
    print("🍏 FOOD FRESHNESS CLASSIFICATION TRAINER")
    print("="*80)
    
    print("\nChoose training mode:")
    print("1.  FULL TRAINING (817 epochs - Best accuracy)")
    print("2.  QUICK TRAINING (10 epochs - Test only)")
    print("3.  CREATE TEST FILES ONLY (No training)")
    print("4.  EXIT")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            print("\n" + "="*80)
            print("STARTING FULL TRAINING...")
            print("This may take 2-4 hours. Don't close the window!")
            print("="*80)
            confirm = input("\nAre you sure? (yes/no): ").lower()
            if confirm in ['yes', 'y', '']:
                main_training()
            else:
                print("Training cancelled.")
        
        elif choice == '2':
            quick_training()
        
        elif choice == '3':
            print("\nCreating test files only...")
            # Simple test files creation
            classes, _, _ = scan_dataset()
            class_info = {
                'classes': classes,
                'class_to_idx': {cls: idx for idx, cls in enumerate(classes)},
                'num_classes': len(classes)
            }
            with open('class_mapping.json', 'w') as f:
                json.dump(class_info, f, indent=2)
            print("Test files created. Run: python simple_backend.py")
        
        elif choice == '4':
            print("Exiting...")
        
        else:
            print("Invalid choice! Please run again.")
    
    except KeyboardInterrupt:
        print("\n\n Training interrupted by user!")
    except Exception as e:
        print(f"\n Error: {e}")