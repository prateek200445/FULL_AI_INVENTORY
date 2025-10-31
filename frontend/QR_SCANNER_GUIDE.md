# QR Code Scanner Feature - Usage Guide

## Overview
The Forecast Dashboard now includes a **QR Code Scanner** that allows you to scan Product ID QR codes directly using your device's camera instead of manually selecting from the dropdown.

## How It Works

### 1. **Location**
- Navigate to the **Forecast** tab in the AI Inventory Management system
- Look for the **Product ID** field in the Forecast Parameters section

### 2. **Accessing the Scanner**
- Next to the Product ID dropdown, you'll see a blue **Camera button** (📷)
- Click this button to open the QR Code Scanner modal

### 3. **Scanning Process**
1. **Grant Camera Permission**: When prompted by your browser, allow camera access
2. **Position QR Code**: Point your camera at the Product ID QR code
3. **Hold Steady**: Keep the QR code within the scanning frame
4. **Auto-Capture**: The scanner will automatically detect and read the code
5. **Auto-Fill**: The scanned Product ID will be instantly populated in the Product ID field
6. **Modal Closes**: The scanner closes automatically after a successful scan

### 4. **Camera Selection**
- If you have multiple cameras (front/back), you can select which one to use
- The scanner remembers your last camera choice

### 5. **Manual Close**
- Click the **X** button in the top-right corner to close the scanner without scanning

## Browser Compatibility

### ✅ Supported Browsers
- Chrome/Edge (Desktop & Mobile) - **Best Performance**
- Firefox (Desktop & Mobile)
- Safari (iOS 11+)
- Opera
- Samsung Internet

### 📱 Mobile Usage
- Works great on smartphones and tablets
- Automatically uses the back camera on phones
- Supports torch/flashlight if available

### 🔒 Security Requirements
- **HTTPS Required**: Camera access only works on HTTPS (secure) connections
- **localhost Exception**: Works on `http://localhost` for development

## QR Code Format

The scanner accepts any standard QR code format. Your Product ID QR codes should contain:
- **Simple Text**: Just the Product ID (e.g., `P001`, `PROD-12345`)
- **Clean Data**: No special formatting needed

Example QR Code Content:
```
P001
```

When scanned, this will set the Product ID field to `P001`.

## Troubleshooting

### Camera Not Working?
1. **Check Permissions**: Ensure you've allowed camera access in your browser
2. **HTTPS**: Make sure you're using HTTPS or localhost
3. **Other Apps**: Close other apps using the camera
4. **Browser Settings**: Check if camera is blocked in browser settings

### QR Code Not Scanning?
1. **Lighting**: Ensure good lighting conditions
2. **Distance**: Hold camera 6-12 inches from the QR code
3. **Focus**: Keep the QR code centered and still
4. **Quality**: Ensure the QR code is clear and not damaged

### Scanner Doesn't Open?
1. **Browser Support**: Check if your browser supports camera access
2. **Console Errors**: Open browser DevTools to check for errors
3. **Permissions**: Camera might be blocked system-wide

## Technical Details

### Libraries Used
- **html5-qrcode**: Robust QR code scanning library
- Features:
  - Multi-format support (QR, barcodes, etc.)
  - Camera selection
  - Auto-focus and torch support
  - Cross-browser compatibility

### Performance
- **FPS**: 10 frames per second scanning
- **Scan Box**: 250x250 pixels optimal size
- **Memory**: Automatically cleans up on close

## Integration with Forecast API

Once scanned:
1. Product ID is set in the form
2. Continue filling other forecast parameters (days, category, region, etc.)
3. Click **Get Forecast** to fetch predictions for that specific product

## Future Enhancements

Potential improvements:
- [ ] Batch QR scanning for multiple products
- [ ] QR code generation for new products
- [ ] History of scanned products
- [ ] Barcode support (UPC, EAN, etc.)
- [ ] Custom scan sound effects

## Example Workflow

```
1. Open Forecast Dashboard
2. Click Camera button next to Product ID
3. Scanner modal opens
4. Grant camera permission (first time only)
5. Point camera at Product QR code
6. Code is scanned: "P001"
7. Modal closes automatically
8. Product ID field now shows "P001"
9. Fill in other parameters (days, category, etc.)
10. Click "Get Forecast"
11. View predictions for Product P001
```

---

**Note**: This feature is designed to work seamlessly with your existing QR code inventory system, making product selection faster and more accurate!
