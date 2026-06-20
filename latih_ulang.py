import pandas as pd
import pickle
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from imblearn.over_sampling import SMOTE

warnings.filterwarnings('ignore')

print("1. Membaca Dataset...")
df = pd.read_csv("2020 Predictive Maintenance Dataset.csv")

X = df[['Rotational speed [rpm]', 'Process temperature [K]', 'Air temperature [K]', 'Torque [Nm]']]
y = df['Machine failure']

print("2. Menyeimbangkan Data AI (SMOTE)...")
smote = SMOTE(random_state=42)
X_seimbang, y_seimbang = smote.fit_resample(X, y)

X_train, X_test, y_train, y_test = train_test_split(X_seimbang, y_seimbang, test_size=0.2, random_state=42)

print("3. Membuat Scaler dan Melatih KNN...")
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)

model_knn = KNeighborsClassifier(n_neighbors=5)
model_knn.fit(X_train_scaled, y_train)

print("4. Menyimpan Otak Baru (.pkl)...")
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
with open('model_terbaik.pkl', 'wb') as f:
    pickle.dump(model_knn, f)

print("✅ SELESAI! Model AI Anda sekarang 100% Cerdas dan Siap Uji.")