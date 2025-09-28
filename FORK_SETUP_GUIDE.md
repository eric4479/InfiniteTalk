# Setting Up Your Own Test Branch for Issue #123 Fix

You're getting the `git checkout fix-model-download-paths` error because this branch only exists locally. Here are multiple ways to set up testing on Runpod:

## Method 1: Fork and Push (Recommended)

### Step 1: Fork the Repository
1. Go to https://github.com/MeiGen-AI/InfiniteTalk
2. Click "Fork" button to create a fork in your account
3. You'll now have `https://github.com/YOUR_USERNAME/InfiniteTalk`

### Step 2: Add Your Fork as Remote and Push
```bash
# In your local InfiniteTalk directory
cd /home/eric/Code/InfiniteTalk

# Add your fork as a remote (replace YOUR_USERNAME)
git remote add fork https://github.com/YOUR_USERNAME/InfiniteTalk.git

# Push the fix branch to your fork
git push fork fix-model-download-paths

# Also push main branch for completeness
git push fork main
```

### Step 3: Test on Runpod
```bash
# On Runpod, clone YOUR fork
git clone https://github.com/YOUR_USERNAME/InfiniteTalk.git
cd InfiniteTalk

# Now this will work!
git checkout fix-model-download-paths

# Run the setup
./scripts/setup_runpod.sh
```

## Method 2: Create Patch File (Alternative)

If you prefer not to fork, I can create a patch file:

```bash
# Create patch file with all changes
git diff main > issue-123-fix.patch

# Then on Runpod:
git clone https://github.com/MeiGen-AI/InfiniteTalk.git
cd InfiniteTalk
# Apply patch (you'd need to transfer the patch file)
git apply issue-123-fix.patch
```

## Method 3: Direct Branch Creation (Simple)

Create the branch directly on Runpod with the changes:

```bash
# On Runpod
git clone https://github.com/MeiGen-AI/InfiniteTalk.git
cd InfiniteTalk

# Create and switch to test branch
git checkout -b test-issue-123-fix

# Then manually copy the fixed files (I'll provide them)
```

## Which Method Do You Prefer?

**I recommend Method 1** because it's cleanest and lets you:
- Test exactly the same code
- Push additional fixes if needed
- Share the branch easily
- Keep track of changes

Let me know which method you'd like to use and I'll provide the specific commands for your setup!