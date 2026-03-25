<?php
// Ensure session exists (safe to include everywhere)
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$isLoggedIn = isset($_SESSION["account_id"]);
?>

<!-- Navigation Bar -->
<nav class="bg-blue-700 p-4">
    <div class="container mx-auto flex justify-between items-center">
        
        <a href="#" class="text-2xl font-bold hover:text-blue-200">
            Geofencing website
        </a>
        
        <!-- Desktop Navigation -->
        <ul class="hidden space-x-6 lg:flex">

            <li><a href="pairing.php" class="text-lg font-bold hover:text-blue-200">Pairing</a></li>
            <li><a href="alerts.php" class="text-lg font-bold hover:text-blue-200">Alerts</a></li>
            <li><a href="settings.php" class="text-lg font-bold hover:text-blue-200">Settings</a></li>
            <li><a href="geofence.php" class="text-lg font-bold hover:text-blue-200">Set up Geofence</a></li>

        </ul>
        
        <!-- Mobile Menu -->
        <div class="relative inline-block text-left lg:hidden">
            <button type="button"
                class="inline-flex w-full justify-center rounded-md bg-blue-700 px-3 py-2 font-semibold text-white text-3xl hover:bg-blue-200"
                id="menu-button">
                ☰
            </button>

            <!-- Dropdown -->
            <div id="dropdown"
                class="hidden absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg">

                <a href="pairing.php" class="text-gray-700 block px-4 py-2 text-sm">Pairing</a>
                <a href="alerts.php" class="text-gray-700 block px-4 py-2 text-sm">Alerts</a>
                <a href="settings.php" class="text-gray-700 block px-4 py-2 text-sm">Settings</a>
                <a href="geofence.php" class="text-gray-700 block px-4 py-2 text-sm">Set up Geofence</a>

                <?php if ($isLoggedIn): ?>
                    <a href="auth/logout.php" class="text-red-600 block px-4 py-2 text-sm">
                        Logout
                    </a>
                <?php else: ?>
                    <a href="sign_in_page.php" class="text-gray-700 block px-4 py-2 text-sm">
                        Sign In
                    </a>
                <?php endif; ?>

            </div>
        </div>
        
        <!-- Desktop Right Side -->
        <div class="hidden lg:flex items-center">

            <?php if ($isLoggedIn): ?>
                <a href="auth/logout.php"
                   class="mr-4 text-lg font-bold text-red-300 hover:text-red-100">
                   Logout
                </a>
            <?php else: ?>
                <a href="sign_in_page.html"
                   class="mr-4 text-lg font-bold hover:text-blue-200">
                   Sign In
                </a>
            <?php endif; ?>

        </div>

    </div>
</nav>

<script>
document.addEventListener("DOMContentLoaded", () => {
    const menuButton = document.getElementById("menu-button");
    const dropdownMenu = document.getElementById("dropdown");

    if(menuButton){
        menuButton.addEventListener('click', () => {
            dropdownMenu.classList.toggle("hidden");
        });
    }
});
</script>