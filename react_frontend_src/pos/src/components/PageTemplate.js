import React, { Component } from "react"
import { render } from "react-dom"
  
import Footer from "./ui/Footer"
import MainMenu from "./MainMenu"
import Content from "./ui/Content";

const PageTemplate = ({children}) => 
    <div className="wrapper">
        <MainMenu />
        <Content>
            {children}
        </Content>
        {/* <Footer /> */}
    </div>

export default PageTemplate