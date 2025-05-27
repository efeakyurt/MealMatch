
# 🧼 Veriseti Hazırlık Süreci

## 📂 Kaynak Dosya: `1662574418893344.csv`  
## 📁 Son Hâli: `updated_food_dataset.csv`

---

### 🎯 Hedef
İlk veriseti yalnızca yemek isimleri, kategorileri ve açıklamaları içeriyordu. Amacımız bu veri setini kullanıcıların zevkine ve bütçesine göre yemek önerileri sunabilecek duruma getirmekti.

---

## 📊 Uygulanan Veri Manipülasyonları ve Temizleme Adımları

### ✅ 1. Eksik Veri Kontrolü
```python
df = pd.read_csv("1662574418893344.csv")
df.isnull().sum()
```
**Sonuç:** Tüm satırlar doluydu. Eksik veri yoktu. ✅

---

### ✅ 2. `price` Sütunu Eklendi

#### 🎯 Amaç
Kullanıcının belirleyeceği **bütçeye göre filtreleme yapabilmek** için her yemeğe fiyat bilgisi gerekiyordu.

#### 🔧 Uygulanan Yöntem
Yemek türlerine göre 2025 restoran fiyat aralıkları belirlendi:

| C_Type           | Fiyat Aralığı (TL) |
|------------------|--------------------|
| Dessert          | 15 – 40 TL         |
| Healthy Food     | 20 – 50 TL         |
| Indian, Japanese | 30 – 70 TL         |
| Diğer            | 15 – 50 TL         |

```python
def assign_price(row):
    if row['C_Type'] == 'Dessert':
        return round(np.random.uniform(15, 40), 2)
    elif row['C_Type'] == 'Healthy Food':
        return round(np.random.uniform(20, 50), 2)
    elif row['C_Type'] in ['Indian', 'Japanese']:
        return round(np.random.uniform(30, 70), 2)
    else:
        return round(np.random.uniform(15, 50), 2)

df['price'] = df.apply(assign_price, axis=1)
```

---

### ✅ 3. `mapped_type` Sütunu Eklendi

#### 🎯 Amaç
Yemekleri damak zevkine göre filtreleyebilmek için 5 gruba ayırdık:
- sweet
- vegan
- spicy
- savory
- other

#### 🧠 Kategori Atama Kuralları

```python
def map_food_type(row):
    if 'dessert' in row['C_Type'].lower() or any(x in row['Describe'].lower() for x in ['sugar', 'sweet', 'chocolate']):
        return 'sweet'
    elif row['Veg_Non'].lower() == 'veg':
        return 'vegan'
    elif any(x in row['Describe'].lower() for x in ['spicy', 'pepper', 'chilli']):
        return 'spicy'
    elif any(x in row['C_Type'].lower() for x in ['indian', 'chinese', 'thai']):
        return 'savory'
    else:
        return 'other'

df['mapped_type'] = df.apply(map_food_type, axis=1)
```

---

### ✅ 4. Final Kayıt
```python
df.to_csv("updated_food_dataset.csv", index=False)
```

---

## ✅ Sonuç
İlk veri setinden **filtreleme yapılabilen**, **gerçekçi fiyatlar içeren** ve **tat tercihlerine göre kategorize edilmiş** bir veri setine ulaşıldı. Bu veri seti artık MealMatch öneri sisteminde kullanılmaya hazırdır.
