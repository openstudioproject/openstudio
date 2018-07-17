import React from "react";
import ReactDOM from "react-dom";

const Footer = () => 
    <footer className="main-footer">
        <strong>Peacefully powered by <a href="https://www.openstudioproject.com/" target="_blank">OpenStudio</a></strong>. All rights reserved &copy; 
        {new Date().getFullYear()}
        .
    </footer>

export default Footer