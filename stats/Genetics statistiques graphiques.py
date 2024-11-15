import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the JSON data from the file
with open("C:/Users/Utilisateur/Arthur/Cours/A3/Algorithme et optimisation combinatoire/Projet/Théophile/result_genetics.json", "r") as file:
    data = json.load(file)

# Initialize a list to store the results
results = []

# Iterate through the tests in the JSON
for test_name, test_data in data.items():
    test_number = re.search(r'\d+', test_name).group()  # Extract the test number
    
    # Iterate through each parameter configuration
    for param_desc, values in test_data.items():
        # Extract the parameters for Tabu, Genetics, etc.
        match_genetics = re.search(r"Genetics : generations, (\d+) ; population size, (\d+) ; mutation rate, (\d+\.\d+)", param_desc)
        
        if match_genetics:
            generations = int(match_genetics.group(1))
            population_size = int(match_genetics.group(2))
            mutation_rate = float(match_genetics.group(3))
        else:
            generations, population_size, mutation_rate = None, None, None
        
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
                            "Generations": generations,
                            "PopulationSize": population_size,
                            "MutationRate": mutation_rate,
                            "Distance": distance,
                            "Time": time
                        })
                    else:
                        print(f"Warning: Test {test_number} with parameters {generations}, {population_size}, {mutation_rate} missing 'Distance' or 'Time'")
        elif isinstance(values, dict):
            # Check for Distance and Time directly if values is a dictionary
            distance = values.get("Distance")
            time = values.get("Temps")
            if distance is not None and time is not None:
                results.append({
                    "TestNumber": int(test_number),
                    "Generations": generations,
                    "PopulationSize": population_size,
                    "MutationRate": mutation_rate,
                    "Distance": distance,
                    "Time": time
                })
            else:
                print(f"Warning: Test {test_number} with parameters {generations}, {population_size}, {mutation_rate} missing 'Distance' or 'Time'")

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

# Scatter plot for distance based on number of generations
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="Generations", y="Distance", hue="PopulationSize", palette="viridis", s=100)
sns.regplot(data=df, x="Generations", y="Distance", scatter=False, color="blue", line_kws={"linestyle": "dashed"})
plt.title("Distance vs Generations with Regression Line")
plt.xlabel("Number of Generations")
plt.ylabel("Distance")
plt.legend(title="Population Size")
plt.show()

# Scatter plot for distance based on population size
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="PopulationSize", y="Distance", hue="Generations", palette="plasma", s=100)
sns.regplot(data=df, x="PopulationSize", y="Distance", scatter=False, color="green", line_kws={"linestyle": "dotted"})
plt.title("Distance vs Population Size with Regression Line")
plt.xlabel("Population Size")
plt.ylabel("Distance")
plt.legend(title="Generations")
plt.show()

# Scatter plot for time based on number of generations
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="Generations", y="Time", hue="PopulationSize", palette="coolwarm", s=100)
sns.regplot(data=df, x="Generations", y="Time", scatter=False, color="red", line_kws={"linestyle": "dashed"})
plt.title("Execution Time vs Generations with Regression Line")
plt.xlabel("Number of Generations")
plt.ylabel("Execution Time (seconds)")
plt.legend(title="Population Size")
plt.show()

# Scatter plot for time based on population size
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="PopulationSize", y="Time", hue="Generations", palette="cool", s=100)
sns.regplot(data=df, x="PopulationSize", y="Time", scatter=False, color="purple", line_kws={"linestyle": "dotted"})
plt.title("Execution Time vs Population Size with Regression Line")
plt.xlabel("Population Size")
plt.ylabel("Execution Time (seconds)")
plt.legend(title="Generations")
plt.show()
