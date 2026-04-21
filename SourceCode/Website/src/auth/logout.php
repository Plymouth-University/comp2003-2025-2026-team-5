<?php

session_start();

session_destroy();

header("Location: /website/src/sign_in_page.php");