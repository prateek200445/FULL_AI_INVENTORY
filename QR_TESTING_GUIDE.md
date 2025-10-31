# QR Scanner Testing Guide

## 🧪 How to Test the QR Upload Feature

### Method 1: Generate & Upload QR Code (Recommended)

1. **Generate a Test QR Code**:
   - Open `qr-generator-test.html` in your browser (double-click the file)
   - Click one of the preset buttons (P001, P002, etc.) or enter your own Product ID
   - Click "Generate QR Code"
   - Click "Download PNG" to save the QR code image

2. **Test Upload in Your App**:
   - Go to http://localhost:5174
   - Navigate to the **Forecast** tab
   - Click the **Camera button** (📷) next to Product ID
   - Click the **Upload Image** tab
   - Click the upload area or drag & drop the QR code image you downloaded
   - ✅ The Product ID should be automatically filled!

### Method 2: Screenshot Method

1. **Create QR Code Screenshot**:
   - Open `qr-generator-test.html`
   - Generate a QR code for any Product ID
   - Take a screenshot of just the QR code area
   - Save the screenshot

2. **Upload Screenshot**:
   - Go to your Forecast Dashboard
   - Click Camera button → Upload Image tab
   - Upload the screenshot
   - Product ID auto-fills!

### Method 3: Phone Camera → Upload

1. **Generate QR on Computer**:
   - Open `qr-generator-test.html` on your computer
   - Generate and display a QR code

2. **Scan with Phone Camera**:
   - Take a photo of the QR code displayed on your screen using your phone
   - Transfer the photo to your computer (email, cloud storage, etc.)
   - Upload it through the app

## 🎯 Expected Behavior

### ✅ Success Case:
- Upload area shows "Processing Image..."
- Scanner modal closes automatically
- Product ID field is filled with the decoded value
- Console shows: `✅ QR Code successfully decoded from file: P001`
- Console shows: `🎯 QR Scan successful! Product ID: P001`

### ❌ Error Cases:

**1. Invalid Image Type**:
- Error: "Please upload an image file (PNG, JPG, etc.)"
- Solution: Upload PNG, JPG, JPEG, GIF, BMP, or WEBP

**2. No QR Code in Image**:
- Error: "Could not read QR code from this image..."
- Solution: Ensure image contains clear, visible QR code

**3. Blurry/Damaged QR**:
- Error: "Could not read QR code..."
- Solution: Use clearer image or regenerate QR code

## 🔍 Debugging Steps

If upload doesn't work, check:

1. **Browser Console** (F12 → Console tab):
   ```
   Look for:
   ✅ QR Code successfully decoded from file: [value]
   🎯 QR Scan successful! Product ID: [value]
   
   Or errors:
   ❌ Error scanning file: [error details]
   ```

2. **Network Tab** (F12 → Network):
   - No network requests should be made (all processing is client-side)

3. **File Type**:
   - Verify image is .png, .jpg, .jpeg, .gif, .bmp, or .webp
   - Check file isn't corrupted

4. **QR Code Quality**:
   - QR should be at least 100x100 pixels
   - Clear contrast (black on white)
   - Not rotated or distorted

## 📱 Testing with Real Device Camera

1. **Enable Camera Access**:
   - Go to Camera Scan tab
   - Allow camera permissions
   - Point at QR code
   - Should auto-scan

2. **Switch Between Modes**:
   - Camera Scan → for live scanning
   - Upload Image → for pre-captured images

## 🐛 Common Issues & Fixes

### Issue: "Processing Image..." never completes
**Fix**: The QR code might not be detected. Try:
- Better quality image
- Crop image to show only QR code
- Ensure QR code has good contrast

### Issue: Product ID field doesn't update
**Fix**: Check browser console for errors:
```javascript
// Should see these logs:
✅ QR Code successfully decoded from file: P001
🎯 QR Scan successful! Product ID: P001
```

### Issue: Modal doesn't close after upload
**Fix**: This means QR decoding failed. Check error message in red box.

## ✨ Features to Test

- [ ] Upload PNG QR code → Success
- [ ] Upload JPG QR code → Success
- [ ] Upload screenshot → Success
- [ ] Upload non-image file → Error message
- [ ] Upload image without QR → Error message
- [ ] Multiple uploads in a row → Works each time
- [ ] Camera scan → Works
- [ ] Switch between Camera/Upload tabs → Works
- [ ] Close modal with X button → Modal closes
- [ ] Close modal after successful scan → Auto-closes

## 📊 Test Data

Sample Product IDs to test:
```
P001
P002
P003
PROD-001
PROD-12345
SKU-ABC-123
ITEM_001
```

Generate QR codes for each and test upload!

---

**Happy Testing! 🎉**
