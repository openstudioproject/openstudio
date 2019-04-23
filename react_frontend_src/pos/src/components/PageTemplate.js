import React from "react"
  
// add protypes

import Footer from "./ui/Footer"
import MainMenu from "./MainMenu"
import Content from "./ui/Content";
import ErrorScreen from "./ui/ErrorScreen";

// Import toast
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'

const PageTemplate = ({ app_state, children, tools="" }) => 
    (app_state.error) ?
        <ErrorScreen message={app_state.error_message}
                    data={app_state.error_data}/>:
        <div style={{height: "auto", minHeight: "100%"}}>
            <MainMenu />
            <Content title={app_state.current_page_title}
                     subtitle={app_state.current_page_subtitle}
                     tools={tools}>
                {children}
            </Content>
            <ToastContainer autoClose={5000} />
            {/* <Footer /> - No footer for now, it looks cleaner and we have OpenStudio branding in the header anyway */}
        </div>

export default PageTemplate