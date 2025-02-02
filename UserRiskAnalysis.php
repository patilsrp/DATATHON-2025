<?php
// Google Cloud SQL Database Connection
$host = "your-cloud-sql-public-ip"; // Change this to Cloud SQL instance IP
$dbname = "elearning_db";
$username = "your_db_username";
$password = "your_db_password";
$port = "3306"; // Default MySQL port

// Connect to Cloud SQL
$conn = new mysqli($host, $username, $password, $dbname, $port);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Fetch Users from Database
$sql = "SELECT * FROM users";
$result = $conn->query($sql);

$users = [];
while ($row = $result->fetch_assoc()) {
    $users[] = $row;
}

// Convert to JSON for JavaScript
$usersJson = json_encode($users);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Risk Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
    <style>
        body { background-color: #f8f9fa; }
        .card { border-radius: 8px; }
        .user-card { border-left: 5px solid #007bff; transition: 0.3s; }
        .user-card:hover { transform: scale(1.02); }
        .churn-score { font-weight: bold; }
    </style>
</head>
<body>

    <div class="container mt-4">
        <h2 class="text-center mb-4">User Risk Analysis (Churn Segmentation)</h2>

        <!-- Navigation Buttons -->
        <div class="text-center mb-3">
            <a href="dashboard.php" class="btn btn-secondary me-2">Back to Dashboard</a>
            <a href="index.html" class="btn btn-primary me-2">Back to Home</a>
            <a href="AI.html" class="btn btn-success">Go to AI Analysis</a>
        </div>

        <!-- Search and Filter Section -->
        <div class="card p-3 shadow-sm">
            <div class="row">
                <div class="col-md-6">
                    <input type="text" id="searchInput" class="form-control" placeholder="Search by name, email, or subscription type">
                </div>
                <div class="col-md-4">
                    <select id="riskFilter" class="form-select">
                        <option value="all">All Users</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="high-risk">High Risk</option>
                        <option value="low-risk">Low Risk</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button class="btn btn-primary w-100" onclick="filterUsers()">Apply Filter</button>
                </div>
            </div>
        </div>

        <!-- User List -->
        <div class="mt-4">
            <div id="userList" class="row"></div>
        </div>
    </div>

    <script>
        // Users data from PHP
        const users = <?php echo $usersJson; ?>;

        // Display Users
        function displayUsers(filteredUsers) {
            const userList = document.getElementById("userList");
            userList.innerHTML = "";
            filteredUsers.forEach(user => {
                userList.innerHTML += `
                    <div class="col-md-6 mt-3">
                        <div class="card user-card p-3 shadow-sm">
                            <h5>${user.name}</h5>
                            <p><strong>Email:</strong> ${user.email}</p>
                            <p><strong>Subscription:</strong> ${user.subscription}</p>
                            <p><strong>Engagement:</strong> ${user.logins} logins, ${user.courses_completed} courses completed</p>
                            <p><strong>Sentiment:</strong> ${user.sentiment}</p>
                            <p class="churn-score"><strong>Churn Score:</strong> ${user.churn_score}%</p>
                            <p><strong>Gamification Impact:</strong> ${user.gamification}</p>
                        </div>
                    </div>
                `;
            });
        }

        // Filter Users based on input and dropdown
        function filterUsers() {
            const searchInput = document.getElementById("searchInput").value.toLowerCase();
            const riskFilter = document.getElementById("riskFilter").value;

            let filteredUsers = users.filter(user =>
                (user.name.toLowerCase().includes(searchInput) ||
                user.email.toLowerCase().includes(searchInput) ||
                user.subscription.toLowerCase().includes(searchInput)) &&
                (riskFilter === "all" || user.risk === riskFilter)
            );

            displayUsers(filteredUsers);
        }

        // Initial display of all users
        displayUsers(users);
    </script>

</body>
</html>




