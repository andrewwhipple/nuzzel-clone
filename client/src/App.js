import React from 'react'

import logo from './logo.svg';
import './App.css';

// React Bootstrap imports
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';


class LinkList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      links: []
    }

    this.getLinks = this.getLinks.bind(this);
    this.fillTree = this.fillTree.bind(this);

    this.getLinks();

  }

  fillTree() {
    fetch('/api/users/1/fill_tree', {
      method: 'POST'
    }).then((res) => {
      console.log("New tweets grabbed");
    }).catch(() => console.log('Error filling tree'));
  }

  getLinks() {
    fetch('/api/user/1/following_tweets?urls_only=true&time_limit=24', {
      method: 'GET',
    }).then((res) => {
      res.json().then((responseJson) => {
        //console.log(responseJson);
        this.setState(
          {
            links: responseJson
          }
        )
      })
    }).catch(() => console.error('Error in fetching tweets'));
  }
  
  
  
  render() {
    
    let linksArray = [];
    let linksDict = {};
    for (let link in this.state.links) {

      if (this.state.links[link].url in linksDict) {
        let sharers = linksDict[this.state.links[link].url];
        
        if (!sharers.find((sharer) => sharer.username == this.state.links[link].username)) {
          sharers.push(
            {
              "name": this.state.links[link].name,
              "username": this.state.links[link].username,
              "id": this.state.links[link].id
            }
          );
        }
        
        linksDict[this.state.links[link].url] = sharers;

      } else {
        linksDict[this.state.links[link].url] = [
          {
            "name": this.state.links[link].name,
            "username": this.state.links[link].username,
            "id": this.state.links[link].id
          }
          
          
        ];
      }
    
    }

    for (let new_link in linksDict) {
      linksArray.push(<Link key={new_link} link={new_link} sharers={linksDict[new_link]}/>);
    }

    linksArray.sort((first, second) => {
      if (first.props.sharers.length > second.props.sharers.length) {
        return -1;
      } else if (first.props.sharers.length < second.props.sharers.length) {
        return 1;
      } else {
        return 0;
      }
    })

    return (
      <div class="link-list">
        {linksArray}
        <div class="buttons">
          <button type="button" onClick={this.getLinks}>Refresh</button>
          <button type="button" onClick={this.fillTree}>Fill tree</button>
        </div>
        
      </div>
    )
  }
}


class LinkSharer extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div><p>meow</p></div>
    )

  }

}


class Link extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      sharers: ""
    }

    this.getUser = this.getUser.bind(this);

  }
  

  getUser(user_id) {
    fetch('/api/twitter_user/' + user_id, {
      method: 'GET',
    }).then((res) => {
      res.json().then((responseJson) => {
        //console.log(responseJson);
        let new_sharers = this.state.sharers;
        new_sharers = new_sharers + responseJson.name;

        if (2 != this.props.sharers.length - 1) {
          new_sharers = new_sharers + ", "
        }
        this.setState({
          sharers: new_sharers
        });
      })
    }).catch(() => console.error('Error in fetching users'));
  }


  render() {
    let sharer_links = []
    for (var sharer in this.props.sharers) {
      let tweet_url = 'https://twitter.com/' + this.props.sharers[sharer].username + '/status/' + this.props.sharers[sharer].id;
      console.log(tweet_url);
      sharer_links.push(<a href={tweet_url}>{this.props.sharers[sharer].name}</a>)
      if (sharer != this.props.sharers.length - 1) {
          sharer_links.push(", ");
      }

    }

    return (
      <div class="link">
        <Container>
          <Row>
            <Col>
              <p>A link has: </p>
              <ul>
                <li>The link url: <a href={this.props.link}>{this.props.link}</a></li>
              </ul>
            </Col>
            <Col>
              <p>And also:</p>
              <ul>
                <li>The number of people who shared it: {this.props.sharers.length}</li>
                <li>The names of the people who shared it: {sharer_links}</li>  
              </ul>
            </Col>
          </Row>
        </Container>
      </div>
    )
  }

}



function App() {

  
  return (
    <LinkList/>
  );
}

export default App;
