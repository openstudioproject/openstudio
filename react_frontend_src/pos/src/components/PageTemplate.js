import React from "react"
  
import Footer from "./ui/Footer"
import MainMenu from "./MainMenu"
import Content from "./ui/Content";

const PageTemplate = ({ loading, loading_message, children }) => 
    (loading) ?
        <div>Loading... <br />{loading_message}</div> :
        <div className="wrapper">
            <MainMenu />
            <Content>
                {children}
            </Content>
            {/* <Footer /> */}
        </div>
        

export default PageTemplate