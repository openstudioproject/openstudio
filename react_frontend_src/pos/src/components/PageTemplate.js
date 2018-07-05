import React from "react"
  
// add protypes

import Footer from "./ui/Footer"
import MainMenu from "./MainMenu"
import Content from "./ui/Content";

const PageTemplate = ({ app_state, children }) => 
    (!app_state.loaded) ?
        <div>Loading... <br />{app_state.loading_message}</div> :
        <div className="wrapper">
            <MainMenu />
            <Content>
                {children}
            </Content>
            {/* <Footer /> */}
        </div>
        

export default PageTemplate