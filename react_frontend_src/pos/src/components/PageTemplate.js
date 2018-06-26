import React, { Component } from "react"
import { render } from "react-dom"
  

import Footer from "./ui/Footer"
import Header from "./ui/Header"
import Navbar from "./ui/Navbar"
import NavbarHeader from "./ui/NavbarHeader"
import NavbarCollapse from "./ui/NavbarCollapse";
import NavbarNav from "./ui/NavbarNav";

const PageTemplate = ({children}) => 
    <div className="wrapper">
        <Header>
            <Navbar>
                <NavbarHeader />
                <NavbarCollapse>
                    <NavbarNav>

                    </NavbarNav>                
                </NavbarCollapse>
            </Navbar>
        </Header>
        <div class="content-wrapper">
            <section className="content">
                {children}
            </section>
        </div>
        <Footer />
    </div>

export default PageTemplate