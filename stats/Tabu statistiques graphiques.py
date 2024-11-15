import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the JSON data from the file
with open("C:/Users/Utilisateur/Arthur/Cours/A3/Algorithme et optimisation combinatoire/Projet/Théophile/result_tabu.json", "r") as file:
    data = json.load(file)

# Initialize a list to store the results
results = []

# Iterate through the tests in the JSON
for test_name, test_data in data.items():
    test_number = re.search(r'\d+', test_name).group()  # Extract the test number
    
    # Iterate through each parameter configuration
    for param_desc, values in test_data.items():
        # Extract the parameters (length tabu, maximum iteration, etc.)
        match = re.search(r"Tabu : length tabu, (\d+) ; maximum iteration, (\d+) ; number of tests, (\d+)", param_desc)
        if match:
            length_tabu = int(match.group(1))
            max_iterations = int(match.group(2))
            num_tests = int(match.group(3))
        else:
            length_tabu = None
            max_iterations = None
            num_tests = None
        
        # Check if values is a list or dictionary
        if isinstance(values, list):
            # Iterate through each element in the list if values is a list
            for item in values:
                if isinstance(item, dict):
                    # Check for the presence of Distance and Time fields
                    distance = item.get("Distance")
                    time = item.get("Temps")
                    if distance is not None and time is not None:
                        results.append({
                            "TestNumber": int(test_number),
                            "LengthTabu": length_tabu,
                            "MaxIterations": max_iterations,
                            "NumTests": num_tests,
                            "Distance": distance,
                            "Time": time
                        })
                    else:
                        print(f"Warning: Test {test_number} with parameters {length_tabu}, {max_iterations}, {num_tests} missing 'Distance' or 'Time'")
        elif isinstance(values, dict):
            # Check for Distance and Time directly if values is a dictionary
            distance = values.get("Distance")
            time = values.get("Temps")
            if distance is not None and time is not None:
                results.append({
                    "TestNumber": int(test_number),
                    "LengthTabu": length_tabu,
                    "MaxIterations": max_iterations,
                    "NumTests": num_tests,
                    "Distance": distance,
                    "Time": time
                })
            else:
                print(f"Warning: Test {test_number} with parameters {length_tabu}, {max_iterations}, {num_tests} missing 'Distance' or 'Time'")

# Convert the results into a DataFrame for easier analysis
df = pd.DataFrame(results)
print(f"\nTotal number of tests extracted: {len(df)}")
pd.options.display.max_rows = 20  # Adjust to the size you want
print(df)  # Display a preview of the DataFrame

# Configure Seaborn style
sns.set(style="whitegrid")

# Boxplot for distances
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, y="Distance")
plt.title("Boxplot of Distances")
plt.ylabel("Distance")
plt.show()

# Boxplot for time
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, y="Time")
plt.title("Boxplot of Times")
plt.ylabel("Time")
plt.show()

# Scatter plot for distance based on length tabu
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="LengthTabu", y="Distance", hue="MaxIterations", palette="viridis", s=100)
sns.regplot(data=df, x="LengthTabu", y="Distance", scatter=False, color="blue", line_kws={"linestyle": "dashed"})
plt.title("Distance vs Length of Tabu with Regression Line")
plt.xlabel("Length of Tabu")
plt.ylabel("Distance")
plt.legend(title="Max Iterations")
plt.show()

# Scatter plot for distance based on max iterations
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="MaxIterations", y="Distance", hue="LengthTabu", palette="plasma", s=100)
sns.regplot(data=df, x="MaxIterations", y="Distance", scatter=False, color="green", line_kws={"linestyle": "dotted"})
plt.title("Distance vs Max Iterations with Regression Line")
plt.xlabel("Max Iterations")
plt.ylabel("Distance")
plt.legend(title="Length of Tabu")
plt.show()

# Scatter plot for time based on length tabu
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="LengthTabu", y="Time", hue="MaxIterations", palette="coolwarm", s=100)
sns.regplot(data=df, x="LengthTabu", y="Time", scatter=False, color="red", line_kws={"linestyle": "dashed"})
plt.title("Execution Time vs Length of Tabu with Regression Line")
plt.xlabel("Length of Tabu")
plt.ylabel("Execution Time (seconds)")
plt.legend(title="Max Iterations")
plt.show()

# Scatter plot for time based on max iterations
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="MaxIterations", y="Time", hue="LengthTabu", palette="cool", s=100)
sns.regplot(data=df, x="MaxIterations", y="Time", scatter=False, color="purple", line_kws={"linestyle": "dotted"})
plt.title("Execution Time vs Max Iterations with Regression Line")
plt.xlabel("Max Iterations")
plt.ylabel("Execution Time (seconds)")
plt.legend(title="Length of Tabu")
plt.show()
