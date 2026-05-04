<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="./output.css" rel="stylesheet">
    <script>
        // this is code directly from the tailwind documentation: https://tailwindcss.com/docs/dark-mode
        // On page load or when changing themes, best to add inline in `head` to avoid FOUC

        if (
            localStorage.theme === "dark" ||
            (!("theme" in localStorage) &&
            window.matchMedia("(prefers-color-scheme: dark)").matches)
        ) {
            document.documentElement.classList.add("dark");
        } else {
            document.documentElement.classList.remove("dark");
        }
    </script>
</head>

<body class="bg-gray-100 dark:bg-gray-900 text-white font-sans">
    
    <?php include "components/navbar.php"; ?>
    
    <script>
        const menuButton = document.getElementById("menu-button");
        const dropdownMenu = document.querySelector('.absolute.right-0');
    
        menuButton.addEventListener('click', () => {
            dropdownMenu.style.display = dropdownMenu.style.display === 'none' ? 'block' : 'none';
        });
    </script>

    <div class="container mx-auto text-center p-18">
        <hr class="m-8 border-2 border-black dark:border-white">
        <p class="p-4 text-3xl text-black dark:text-white">Colour theme Settings</p>
        <!-- This currently includes light and dark themes but should also have a high contrast theme in the future -->
        <div class="p-4">
            <button
            onclick="setLightMode()"
            class="px-4 py-2 rounded-lg bg-white text-gray-900 border hover:bg-gray-400 text-lg"
            >
            Light
            </button>
        
            <button
            onclick="setDarkMode()"
            class="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-700 text-lg"
            >
            Dark
            </button>
        
            <button
            onclick="setSystemMode()"
            class="px-4 py-2 rounded-lg bg-gray-200 text-gray-900 hover:bg-gray-400 text-lg"
            >
            System
            </button>
        </div>
        <hr class="m-8 border-2 border-black dark:border-white">
        <p class="p-4 text-3xl text-black dark:text-white">Cookie policy</p>
        <p class="p-4 text-xl text-black dark:text-white">This Proof of concept website only uses necessary cookies to enable the core features of the project, the website will not function without them.</p>
        
    </div>
    
    <script>
        function setLightMode() {
            localStorage.theme = "light";
            document.documentElement.classList.remove("dark");
        }

        function setDarkMode() {
            localStorage.theme = "dark";
            document.documentElement.classList.add("dark");
        }

        function setSystemMode() {
            localStorage.removeItem("theme");

            if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
                document.documentElement.classList.add("dark");
            } else {
                document.documentElement.classList.remove("dark");
            }
        }
        </script>

</body>
</html>