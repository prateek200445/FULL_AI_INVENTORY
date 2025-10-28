# Fine-Tuning System Documentation

## 🎯 Overview

The system has been upgraded from **full retraining** to **incremental fine-tuning**. This means:

- ✅ **New data is merged** with existing dataset
- ✅ **LSTM model is fine-tuned** (continues learning from existing weights)
- ✅ **Prophet model retrains** normally (as before)
- ✅ **Model auto-reloads** in FastAPI without server restart
- ✅ **Immediate predictions** using the updated fine-tuned model

---

## 🔧 What Changed

### 1. **model.py** - Added Fine-Tuning Support

#### **LSTMModel.train_with_progress()** - Now supports `fine_tune` parameter

```python
def train_with_progress(self, data, progress_callback=None, epochs=50, batch_size=32, fine_tune=False):
```

**How it works:**

- **`fine_tune=False`** (default): Rebuilds LSTM from scratch (old behavior)
- **`fine_tune=True`**: 
  - Attempts to load existing model weights from `lstm_model_retrained.h5`
  - If found, continues training from those weights
  - If not found, falls back to building new model
  - After training, saves updated weights automatically

**Progress Messages:**
- "Loading existing LSTM model for fine-tuning..."
- "✅ Existing model loaded, continuing training..."
- "Fine-tuning existing model in memory..."
- "✅ Fine-tuned model saved successfully"

---

#### **InventoryForecastModel.train()** - Propagates `fine_tune` parameter

```python
def train(self, data, progress_callback=None, fine_tune=False):
```

- Passes `fine_tune` to LSTM training
- Shows contextual messages: "Fine-tuning" vs "Training"
- Prophet always retrains (fine-tuning not applicable)

---

#### **retrain_model_with_queue()** - Now uses fine-tuning by default

```python
def retrain_model_with_queue(new_data_path: str, q: Queue, epochs=50, batch_size=32, fine_tune=True):
```

**Changes:**
- Default `fine_tune=True` for incremental learning
- Progress message: "🔄 Initializing fine-tuning mode..."
- Merges new CSV with existing data
- Saves combined dataset to `large_dataset.csv`
- Passes `fine_tune=True` to model training

---

#### **retrain_model()** - Non-streaming version also supports fine-tuning

```python
def retrain_model(new_data_path: str, fine_tune=True):
```

Same behavior as `retrain_model_with_queue()` but without streaming progress.

---

### 2. **main.py** (FastAPI) - Auto Model Reloading

#### **New Background Watcher**

A background task runs every 2 seconds checking if model files have been updated:

```python
async def model_file_watcher():
    """Background task that periodically checks for model file updates."""
    while True:
        await asyncio.sleep(2)  # Check every 2 seconds
        reload_global_model_if_needed()
```

**Files watched:**
- `lstm_model_retrained.h5` (LSTM weights)
- `lstm_scaler.pkl` (MinMax scaler)
- `prophet_model.pkl` (Prophet model)

#### **Auto-Reload on File Change**

```python
def reload_global_model_if_needed():
    """Check if model files have been updated and reload GLOBAL_MODEL if necessary."""
```

**How it works:**
1. Compares current file modification times with cached times
2. If any file changed:
   - Creates new `InventoryForecastModel()`
   - Loads from disk: `new_model.load(prophet, lstm, scaler)`
   - Updates `model.GLOBAL_MODEL` with new instance
   - Prints: "🔄 Detected model file changes, reloading..."
   - Prints: "✅ Model reloaded successfully!"

#### **Forecast Endpoint Enhancement**

```python
@app.post("/forecast")
async def get_forecast(request: ForecastRequest):
    # Check if model files have been updated before forecasting
    reload_global_model_if_needed()
    
    # ... rest of forecast logic
```

**Before each forecast:**
- Checks if models updated
- Reloads if needed
- Uses latest fine-tuned model

---

### 3. **app.py** (Flask) - No changes needed

The Flask `/retrain` endpoint automatically uses the updated `retrain_model_with_queue()` with fine-tuning enabled.

---

## 🚀 How to Use

### **Step 1: Start Both Servers**

**Terminal 1 - Flask (retraining server):**
```bash
python app.py
```
Runs on `http://localhost:8000`

**Terminal 2 - FastAPI (forecasting server):**
```bash
uvicorn main:app --port 8001
```
Runs on `http://localhost:8001`

---

### **Step 2: Upload New Data**

Use the HTML test page or cURL:

```bash
curl -X POST http://localhost:8000/retrain \
  -F "file=@your_new_data.csv"
```

**Or use the test page:**
```
http://localhost:8000/retrain-page
```

---

### **Step 3: Watch Fine-Tuning Progress**

You'll see streaming messages like:

```
Reading uploaded CSV...
Merging datasets...
Saving combined dataset...
Preparing data for training...
🔄 Initializing fine-tuning mode...
Starting Prophet training...
Prophet training complete
Starting LSTM fine-tuning...
Loading existing LSTM model for fine-tuning...
✅ Existing model loaded, continuing training...
LSTM epoch 1/50 - loss=0.0234
LSTM epoch 2/50 - loss=0.0198
...
LSTM epoch 50/50 - loss=0.0045
✅ Fine-tuned model saved successfully
LSTM fine-tuning complete
Saving model artifacts...
✅ Success!
```

---

### **Step 4: FastAPI Auto-Reloads**

Within 2 seconds, you'll see in FastAPI terminal:

```
🔄 Detected model file changes, reloading...
✅ Model reloaded successfully!
```

---

### **Step 5: Test Forecast**

**No restart needed!** Immediately test:

```bash
curl -X POST http://localhost:8001/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "days": 7,
    "product_id": "P021"
  }'
```

**Or use the interactive docs:**
```
http://localhost:8001/docs
```

---

## 🧪 Testing Script

Run the comprehensive test:

```bash
python test_fine_tuning.py
```

**This script:**
1. Creates test data with new product P021
2. Uploads to Flask `/retrain` endpoint
3. Shows fine-tuning progress messages
4. Waits for FastAPI auto-reload
5. Tests forecast for P021
6. Displays results

---

## 📊 Fine-Tuning vs Full Retrain

| Feature | Full Retrain (Old) | Fine-Tuning (New) |
|---------|-------------------|-------------------|
| **LSTM Weights** | Rebuilt from scratch | Continue from saved weights |
| **Training Time** | Longer (starts at epoch 0) | Faster (continues learning) |
| **Data Loss** | Previous learning lost | Previous learning preserved |
| **New Data** | Merged but re-learned | Merged and incrementally learned |
| **Prophet** | Always retrained | Always retrained (same) |
| **Server Restart** | Required | Not required ✅ |

---

## 🎯 Key Benefits

### 1. **Incremental Learning**
- Model doesn't "forget" previous patterns
- Adapts to new data while retaining old knowledge
- More stable predictions over time

### 2. **Faster Retraining**
- Fine-tuning typically faster than full retrain
- Less computational overhead
- Better for frequent updates

### 3. **Zero-Downtime Updates**
- FastAPI automatically detects model changes
- Reloads in background (2-second polling)
- No manual restart needed
- Forecasts always use latest model

### 4. **Seamless Integration**
- Upload CSV → Fine-tune → Auto-reload → Forecast
- End-to-end automated workflow
- No manual intervention required

---

## 🔍 File Structure

```
project/
├── model.py                    # ML models with fine-tuning support
├── app.py                      # Flask retraining server
├── main.py                     # FastAPI forecast server (auto-reload)
├── large_dataset.csv           # Combined dataset (auto-updated)
├── lstm_model_retrained.h5     # LSTM weights (fine-tuned)
├── lstm_scaler.pkl             # MinMax scaler
├── prophet_model.pkl           # Prophet model
├── model_meta.json             # Training metadata
├── test_fine_tuning.py         # Comprehensive test script
└── uploads/                    # Uploaded CSV files
```

---

## 🐛 Troubleshooting

### **"No existing model found"**
- Expected on first run
- System builds new model
- Subsequent uploads will fine-tune

### **"Failed to reload model"**
- Check if all 3 model files exist
- Verify file permissions
- Check FastAPI logs for errors

### **FastAPI not detecting changes**
- Wait 2-3 seconds (polling interval)
- Check file modification times
- Restart FastAPI if needed

### **"Could not load existing model"**
- Model file might be corrupted
- System falls back to building new model
- Previous weights will be overwritten

---

## 📝 Code Examples

### **Manual Fine-Tuning (Python)**

```python
import model

# Load existing model
inv_model = model.InventoryForecastModel()
inv_model.load(
    model.PROPHET_MODEL_PATH,
    model.LSTM_WEIGHTS_PATH,
    model.LSTM_SCALER_PATH
)

# Prepare new data
prophet_df = new_data.groupby('date')['sales'].sum().reset_index()
prophet_df.columns = ['ds', 'y']

# Fine-tune
inv_model.train(prophet_df, fine_tune=True)

# Save
inv_model.save(
    model.PROPHET_MODEL_PATH,
    model.LSTM_WEIGHTS_PATH,
    model.LSTM_SCALER_PATH
)
```

### **Full Retrain (when needed)**

```python
# Sometimes you want to start fresh
inv_model.train(prophet_df, fine_tune=False)
```

---

## 🎉 Summary

Your system now:

✅ **Combines** past + new data during retraining  
✅ **Fine-tunes** LSTM model instead of full retrain  
✅ **Retrains** Prophet normally  
✅ **Saves** model and reloads seamlessly  
✅ **Auto-detects** model updates in FastAPI  
✅ **Uses** latest fine-tuned version automatically  
✅ **Requires** no restart after retraining  

**Result:** Upload CSV → Model fine-tunes → FastAPI auto-reloads → Forecast with updated model → All in <1 minute! 🚀
