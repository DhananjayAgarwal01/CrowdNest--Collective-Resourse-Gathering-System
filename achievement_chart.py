import matplotlib.pyplot as plt
import numpy as np

# Achievement data
categories = [
    'User Management', 
    'Donation Management', 
    'Donation Request Workflow', 
    'Database Interaction', 
    'Communication System', 
    'Security Enhancements', 
    'UI/UX Improvements'
]
achievements = [100, 90, 90, 100, 95, 100, 95]

# Create the chart
plt.figure(figsize=(10, 6))
plt.bar(categories, achievements, color='#4CAF50')
plt.title('CrowdNest Project Achievements', fontsize=15)
plt.xlabel('Project Components', fontsize=12)
plt.ylabel('Achievement Percentage', fontsize=12)
plt.ylim(0, 110)  # Set y-axis limit
plt.xticks(rotation=45, ha='right')

# Add percentage labels on top of each bar
for i, v in enumerate(achievements):
    plt.text(i, v + 3, str(v)+'%', ha='center', fontweight='bold')

# Add overall project completion
plt.axhline(y=95, color='r', linestyle='--', label='Overall Project Completion')
plt.legend()

plt.tight_layout()
plt.savefig('c:\\Users\\dhana\\Downloads\\sem4mini\\CrowdNest--Collective-Resourse-Gathering-System\\achievement_chart.png', dpi=300)
plt.close()

print("Achievement chart has been saved as achievement_chart.png")
