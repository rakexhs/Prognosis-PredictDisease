
# Importing libraries
import numpy as np
import pandas as pd
from scipy.stats import mode
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# %matplotlib inline

# Reading the train.csv by removing the
# last column since it's an empty column
DATA_PATH = "dataset/Training.csv"
data = pd.read_csv(DATA_PATH).dropna(axis = 1)
data.columns = [col.upper() for col in data.columns]
# Checking whether the dataset is balanced or not
disease_counts = data["PROGNOSIS"].value_counts()
temp_df = pd.DataFrame({
	"Disease": disease_counts.index,
	"Counts": disease_counts.values
})

# plt.figure(figsize = (18,8))
# sns.barplot(x = "Disease", y = "Counts", data = temp_df)
# plt.xticks(rotation=90)
# plt.show()

# Encoding the target value into numerical
# value using LabelEncoder
encoder = LabelEncoder()
data["PROGNOSIS"] = encoder.fit_transform(data["PROGNOSIS"])

X = data.iloc[:,:-1]
y = data.iloc[:, -1]
X_train, X_test, y_train, y_test =train_test_split(
X, y, test_size = 0.2, random_state = 24)

# print(f"Train: {X_train.shape}, {y_train.shape}")
# print(f"Test: {X_test.shape}, {y_test.shape}")

# Defining scoring metric for k-fold cross validation
def cv_scoring(estimator, X, y):
	return accuracy_score(y, estimator.predict(X))

# Initializing Models
models = {
	"SVC":SVC(),
	"Gaussian NB":GaussianNB(),
	"Random Forest":RandomForestClassifier(random_state=18)
}

# Producing cross validation score for the models
for model_name in models:
	model = models[model_name]
	scores = cross_val_score(model, X, y, cv=10, n_jobs=1, scoring=cv_scoring)
	# print("=="*30)
	# print(model_name)
	# print(f"Scores: {scores}")
	# print(f"Mean Score: {np.mean(scores)}")

# Training and testing SVM Classifier
svm_model = SVC()
svm_model.fit(X_train, y_train)
preds = svm_model.predict(X_test)

# print(f"Accuracy on train data by SVM Classifier\
# : {accuracy_score(y_train, svm_model.predict(X_train))*100}")

# print(f"Accuracy on test data by SVM Classifier\
# : {accuracy_score(y_test, preds)*100}")
cf_matrix = confusion_matrix(y_test, preds)
# plt.figure(figsize=(12,8))
sns.heatmap(cf_matrix, annot=True)
# plt.title("Confusion Matrix for SVM Classifier on Test Data")
# plt.show()

# Training and testing Naive Bayes Classifier
nb_model = GaussianNB()
nb_model.fit(X_train, y_train)
preds = nb_model.predict(X_test)
# print(f"Accuracy on train data by Naive Bayes Classifier\
# : {accuracy_score(y_train, nb_model.predict(X_train))*100}")

# print(f"Accuracy on test data by Naive Bayes Classifier\
# : {accuracy_score(y_test, preds)*100}")
cf_matrix = confusion_matrix(y_test, preds)
# plt.figure(figsize=(12,8))
sns.heatmap(cf_matrix, annot=True)
# plt.title("Confusion Matrix for Naive Bayes Classifier on Test Data")
# plt.show()

# Training and testing Random Forest Classifier
rf_model = RandomForestClassifier(random_state=18)
rf_model.fit(X_train, y_train)
preds = rf_model.predict(X_test)
# print(f"Accuracy on train data by Random Forest Classifier\
# : {accuracy_score(y_train, rf_model.predict(X_train))*100}")

# print(f"Accuracy on test data by Random Forest Classifier\
# : {accuracy_score(y_test, preds)*100}")

cf_matrix = confusion_matrix(y_test, preds)
# plt.figure(figsize=(12,8))
sns.heatmap(cf_matrix, annot=True)
# plt.title("Confusion Matrix for Random Forest Classifier on Test Data")
# plt.show()

DATA_PATH = "dataset/Training.csv"
data = pd.read_csv(DATA_PATH).dropna(axis=1)

# Convert column names to uppercase
data.columns = [col.upper() for col in data.columns]
# Training the models on whole data
final_svm_model = SVC()
final_nb_model = GaussianNB()
final_rf_model = RandomForestClassifier(random_state=18)
final_svm_model.fit(X, y)
final_nb_model.fit(X, y)
final_rf_model.fit(X, y)

# Reading the test data
test_data = pd.read_csv("./dataset/Testing.csv").dropna(axis=1)
test_data.columns = [col.upper() for col in test_data.columns]

test_X = test_data.iloc[:, :-1]
test_Y = encoder.transform(test_data.iloc[:, -1])

# Making prediction by take mode of predictions
# made by all the classifiers
svm_preds = final_svm_model.predict(test_X)
nb_preds = final_nb_model.predict(test_X)
rf_preds = final_rf_model.predict(test_X)

final_preds = [mode([i,j,k])[0][0] for i,j,
			k in zip(svm_preds, nb_preds, rf_preds)]

# print(f"Accuracy on Test dataset by the combined model\
# : {accuracy_score(test_Y, final_preds)*100}")

cf_matrix = confusion_matrix(test_Y, final_preds)
# plt.figure(figsize=(12,8))

sns.heatmap(cf_matrix, annot = True)
# plt.title("Confusion Matrix for Combined Model on Test Dataset")
# plt.show()
symptoms = X.columns.values

# Creating a symptom index dictionary to encode the
# input symptoms into numerical form
symptom_index = {}
for index, value in enumerate(symptoms):
    symptom = value.strip().upper().replace("_", " ")  # Convert symptom name to all caps, remove leading/trailing spaces, and replace underscores with spaces
    symptom = " ".join(symptom.split())  # Replace multiple spaces with a single space
    symptom_index[symptom] = index

data_dict = {
	"symptom_index":symptom_index,
	"predictions_classes":encoder.classes_
}
# Defining the Function
# Input: string containing symptoms separated by commas
# Output: Generated predictions by models
def predictDisease(symptoms):
	symptoms = [symptom.strip().upper() for symptom in symptoms.split(",")]
	print(data_dict)
	# creating input data for the models
	input_data = [0] * len(data_dict["symptom_index"])
	for symptom in symptoms:
		index = data_dict["symptom_index"][symptom]
		input_data[index] = 1
	# reshaping the input data and converting it
	# into suitable format for model predictions
	input_data = np.array(input_data).reshape(1,-1)

	# generating individual outputs
	rf_prediction = data_dict["predictions_classes"][final_rf_model.predict(input_data)[0]]
	nb_prediction = data_dict["predictions_classes"][final_nb_model.predict(input_data)[0]]
	svm_prediction = data_dict["predictions_classes"][final_svm_model.predict(input_data)[0]]

	# making final prediction by taking mode of all predictions
	final_prediction = mode([rf_prediction, nb_prediction, svm_prediction])[0][0]
	predictions = {
		"rf_model_prediction": rf_prediction,
		"naive_bayes_prediction": nb_prediction,
		"svm_model_prediction": svm_prediction,
		"final_prediction":final_prediction
	}
	print(final_prediction)
	print(rf_prediction)
	print(svm_prediction)
	print(nb_prediction)
	
	if rf_prediction!=svm_prediction and rf_prediction!=nb_prediction:
		combined_prediction = f"{rf_prediction} || {nb_prediction} || {svm_prediction}"
		return combined_prediction
	elif final_prediction == "AIDS" or final_prediction == "Heart attack":
		return "Try other symptoms"
	else:
		return final_prediction





# Testing the function
# print(predictDisease("Itching,Shivering,Chills"))
# if __name__ == "__main__":
#     # Read symptoms from command-line arguments (skip the first argument, which is the script name)
#     symptoms_list = sys.argv[1:]  # Get the list of symptoms from command-line arguments
#     symptoms = [symptom.capitalize() for symptom in symptoms_list]
#     fsymptoms = ",".join(symptoms)
#     prediction = predictDisease(fsymptoms)
#     print(prediction)
#     sys.stdout.flush()

app = Flask(__name__)
CORS(app)
@app.route('/predict', methods=['POST'])
def predict_symptoms():

	symptoms = request.form.get('symptoms')
	symptomss = symptoms.split(",")
	for i in range(len(symptomss)):
		symptomss[i] = symptomss[i].strip().upper()
	capitalized_string = ",".join(symptomss)
	prediction = predictDisease(capitalized_string)
    # Return the prediction as a JSON response
	return jsonify({"prediction": prediction})
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3500)