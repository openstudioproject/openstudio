import React, {Component} from "react"
import ContentHeader from './ContentHeader'

const initialStyle = {
    // The AdminLTE function handling this doens't seem to be kicked off.
    // so we're setting the height of the content-wrapper manually
    // 50 is the Height of the navigation header
    // 51 is the height of the footer
    minHeight: window.innerHeight - 50
}


class Content extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    componentWillMount() {
        this.resize()
    }

    initialStyle = {minHeight: window.innerHeight - 50}

    resize = () => {
        this.setState({content_height: window.innerHeight - 93})
    }

    componentDidMount() {
        window.addEventListener('resize', this.resize)
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.resize)
    }
        
    render() {
        const title = this.props.title
        const subtitle = this.props.subtitle
        const children = this.props.children

        return (
            <div className="content-wrapper" style={this.initialStyle}>
                <ContentHeader title={title} subtitle={subtitle} />
                <section className="content" style={{height: this.state.content_height}}>
                    {children} 
                </section>
            </div>
        )
    }
}

export default Content