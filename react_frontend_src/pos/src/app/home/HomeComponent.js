import React, { Component } from "react"
import PageTemplate from "../../components/PageTemplate"

class homeComponent extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    // componentWillMount() {
    //     this.props.setLoading(true)
    // }

    componentDidMount() {
        setTimeout(() => this.props.setLoadingMessage('phase 1'), 0)
        setTimeout(() => this.props.setLoadingMessage('phase 2'), 1000)
        setTimeout(() => this.props.setLoadingMessage('phase 3'), 2500)
        // ready...
        setTimeout(() => this.props.setLoading(false), 3000)
        setTimeout(() => this.props.setLoadingMessage('Loading done!'), 3500)
        
    }

    render() {
        return (
            <PageTemplate loading={this.props.app.loading}
                          loading_message={this.props.app.loading_message}>
            <section className="Welcome">
                <div>Welcome page</div>
                <div>{this.props.app.loading}</div>
                <div>{this.props.app.loading_message}</div>
            </section>
            </PageTemplate>
        )
    }
}

export default homeComponent
