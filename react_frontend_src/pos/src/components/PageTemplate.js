import React from "react"
  
// add protypes

import Footer from "./ui/Footer"
import MainMenu from "./MainMenu"
import Content from "./ui/Content";
import ErrorScreen from "./ui/ErrorScreen";

const PageTemplate = ({ app_state, children }) => 
    (app_state.error) ?
        <ErrorScreen message={app_state.error_message}
                    data={app_state.error_data}/>:
        <div style={{height: "auto", minHeight: "100%"}}>
            <MainMenu />
            <Content title={app_state.current_page_title}>
                {children}
            </Content>
            {/* <Footer /> - No footer for now, it looks cleaner and we have OpenStudio branding in the header anyway */}
        </div>

export default PageTemplate