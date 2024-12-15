## **International Football Data Dashboard**

### **Description**
The **International Football Data Dashboard** is an interactive web-based dashboard designed to analyze and visualize football match data from international competitions. Built with **Dash** and **Plotly**, this dashboard provides meaningful insights into team performance, goal distribution, match outcomes, and other key football metrics in an intuitive and engaging way. 

### **Features**
1. **Team-Specific Analysis**:  
   Select any international football team to explore its performance metrics, including goals scored, goals conceded, and penalty shootout wins.  

2. **Interactive Visualizations**:  
   - **Goals Scored by Location and Halves**: Sunburst chart showcasing goals scored at home, away, and in different halves of the match.  
   - **Goals and Unique Scorers Per Minute**: Bar and line chart highlighting the distribution of goals and unique goal scorers across match minutes.  
   - **Performance Metrics Radar Chart**: Radar chart displaying key team performance statistics like win rate, loss rate, and penalties scored.  
   - **3D Surface Chart**: A dynamic surface chart visualizing team metrics such as total goals, clean sheets, and matches played.  
   - **Goal Contribution Bubble Chart**: Scatter plot showing goal contributions over match minutes and years, with bubble sizes representing goal significance.  

3. **Optimized Layout**:  
   All charts and components are neatly arranged to fit within a single page without scrolling, ensuring an improved user experience.

4. **User-Friendly Interface**:  
   - **Dropdown Menu**: Easily switch between teams to view their performance.  
   - **Tooltips and Hover Info**: Hover over data points to access detailed insights.

---

### **Technologies Used**
- **Python**  
- **Dash** and **Plotly** for building and visualizing interactive charts  
- **Pandas** for data manipulation  
- **Gunicorn** for production deployment  

---

### **Use Cases**
- Analyzing football team performance in international competitions  
- Exploring trends in goal scoring patterns  
- Gaining insights into match outcomes and team statistics  

---

### **Setup Instructions**
1. Clone this repository:  
   ```bash
   git clone https://github.com/your-username/international-football-dashboard.git
   cd international-football-dashboard
   ```

2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:  
   ```bash
   python dashboard.py
   ```

4. Access the app at:  
   `http://127.0.0.1:8050`

---

### **Data Sources**
- **Results Data**: International football match results.  
- **Goalscorers Data**: Goal details including scorers, minutes, and penalty info.  
- **Shootouts Data**: Penalty shootout results.  

---

### **Contributing**
Feel free to contribute by reporting issues, suggesting enhancements, or submitting pull requests.  

---

### **Contact**
For queries or feedback, reach out to:  
📧 kartheesavela2182@gmail.com 

---
