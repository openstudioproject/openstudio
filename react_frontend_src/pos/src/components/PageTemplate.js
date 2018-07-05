import React from "react"
  
// add protypes

import Footer from "./ui/Footer"
import MainMenu from "./MainMenu"
import Content from "./ui/Content";
import LoadingScreen from "./ui/LoadingScreen";

const PageTemplate = ({ app_state, children }) => 
    (!app_state.loaded) ?
        <LoadingScreen progress={app_state.loading_progress}
                       message={app_state.loading_message}/> :
        <div>
            <MainMenu />
            <Content title={app_state.current_page_title}>
                {children}
            </Content>
        </div>
        

export default PageTemplate