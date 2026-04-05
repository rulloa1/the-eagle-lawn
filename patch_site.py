import base64, os, sys

# Read the logo image provided by user and convert to base64
# The logo is the lawn mower image pasted by user
# We'll reference the image file path passed as arg 1
logo_path = sys.argv[1] if len(sys.argv) > 1 else None

print("Reading index.html...")
with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print(f"File size: {len(content)} chars")

# --- 1. Replace the leaf SVG logo with the new lawn mower image ---
OLD_LOGO = '<div data-loc="client/src/pages/Home.tsx:92" class="w-10 h-10 bg-primary rounded-full flex items-center justify-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-leaf w-6 h-6 text-primary-foreground" data-loc="client/src/pages/Home.tsx:93"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path></svg></div>'

if logo_path and os.path.exists(logo_path):
    with open(logo_path, 'rb') as img_f:
        img_data = img_f.read()
    # Detect format
    if logo_path.lower().endswith('.png'):
        mime = 'image/png'
    elif logo_path.lower().endswith('.jpg') or logo_path.lower().endswith('.jpeg'):
        mime = 'image/jpeg'
    else:
        mime = 'image/png'
    b64 = base64.b64encode(img_data).decode('utf-8')
    NEW_LOGO = f'<img src="data:{mime};base64,{b64}" alt="The Eagle Lawn Services Logo" style="width:44px;height:44px;object-fit:contain;border-radius:50%;">'
else:
    # Fallback: use a simple lawn mower emoji SVG placeholder if no image provided
    NEW_LOGO = '<div style="width:44px;height:44px;background:#2d5a27;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;">🌿</div>'
    print("WARNING: No logo image found, using fallback")

if OLD_LOGO in content:
    content = content.replace(OLD_LOGO, NEW_LOGO, 1)
    print("✅ Logo replaced successfully")
else:
    print("❌ Logo target not found exactly - trying partial match...")
    # Try simpler match on the leaf SVG
    partial = 'lucide-leaf w-6 h-6 text-primary-foreground'
    idx = content.find(partial)
    if idx >= 0:
        # Find the enclosing div start
        div_start = content.rfind('<div', 0, idx)
        # Find closing </div> after the svg
        svg_end = content.find('</svg>', idx)
        div_end = content.find('</div>', svg_end) + len('</div>')
        old_chunk = content[div_start:div_end]
        print(f"Found partial at {div_start}:{div_end}")
        content = content[:div_start] + NEW_LOGO + content[div_end:]
        print("✅ Logo replaced via partial match")
    else:
        print("❌ Could not find logo SVG")

# --- 2. Remove the Manus previewer root element ---
MANUS_ROOT = '<div id="manus-previewer-root" data-manus-selector-input="true"></div>'
if MANUS_ROOT in content:
    content = content.replace(MANUS_ROOT, '', 1)
    print("✅ Manus previewer root removed")
else:
    print("❌ manus-previewer-root not found (may already be gone)")

# --- 3. Remove the Manus script tag ---
# The huge script that starts around position 6M that has the Manus watermark
# Find the <script> that contains 'manus-previewer-root","contentRoot'
MANUS_MARKER = 'manus-previewer-root","contentRoot'
manus_script_idx = content.find(MANUS_MARKER)
if manus_script_idx >= 0:
    # Find opening <script> before this
    script_open = content.rfind('<script', 0, manus_script_idx)
    script_open_end = content.find('>', script_open) + 1
    # Find closing </script> after this
    script_close_start = content.find('</script>', manus_script_idx)
    script_close_end = script_close_start + len('</script>')
    manus_script = content[script_open:script_close_end]
    print(f"Found Manus script: {script_open} to {script_close_end} ({len(manus_script)} chars)")
    content = content[:script_open] + content[script_close_end:]
    print("✅ Manus script removed")
else:
    print("❌ Manus script marker not found")

# --- 4. Also remove the plasmo-csui extension element at top of body ---
PLASMO = '<plasmo-csui id="copystyle"></plasmo-csui>'
if PLASMO in content:
    content = content.replace(PLASMO, '', 1)
    print("✅ plasmo-csui removed")

# --- 5. Write output ---
print("Writing patched index.html to public/index.html...")
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ Done! public/index.html written.")
print(f"New file size: {len(content)} chars")
