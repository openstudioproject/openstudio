import React from "react"
import ContentHeader from './ContentHeader'

const initialStyle = {
    // The AdminLTE function handling this doens't seem to be kicked off.
    // so we're setting the height of the content-wrapper manually
    // 50 is the Height of the navigation header
    // 51 is the height of the footer
    minHeight: window.innerHeight - 50,
    height: "auto"
}

const Content = ({title, children}) =>
    <div className="content-wrapper" style={initialStyle}>
        <ContentHeader title={title} />
        <section className="content">
            {children} 
        </section>
    </div>

export default Content