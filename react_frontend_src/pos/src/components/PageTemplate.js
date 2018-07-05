import React from "react"
  
// add protypes

import Footer from "./ui/Footer"
import MainMenu from "./MainMenu"
import Content from "./ui/Content";
import LoadingScreen from "./ui/LoadingScreen";

const PageTemplate = ({ app_state, children }) => 
    (!app_state.loaded) ?
        <LoadingScreen message={app_state.loading_message}/> :
        // <div>Loading... <br />{app_state.loading_message}</div> :
        <div className="wrapper">
            <MainMenu />
            <Content title={app_state.current_page_title}>
                {children}
            </Content>
            {/* <Footer /> */}
        </div>
        

export default PageTemplate