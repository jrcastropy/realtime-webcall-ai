import { Container, Row, Col, Image, Button } from "react-bootstrap";
import { Telephone } from "react-bootstrap-icons";

const WebCall = () => {
    return (
        <>
            <Container fluid>
                <Row className="aligh-items-center justify-content-center vh-100">
                    <Col xs={12} md={5} xl={4} className="m-auto p-4 padCustom rounded rounded-5 align-items-center justify-content-center">
                        <div className="bg-dark text-white rounded rounded-5 align-items-center justify-content-center d-flex flex-column">
                            <h3 className="my-5">Incoming Call</h3>
                            <Image className="my-3" src="https://placehold.jp/300x300.png" roundedCircle fluid />
                            <h4 className="mt-3 mb-0">Katy Perry</h4>
                            <p>+639-966-777</p>
                            <div className="my-5 d-flex">
                                <Button variant="success" size="lg" className="btn-block btn-lg px-5">
                                    <Telephone size={30} />
                                </Button>
                            </div>
                        </div>
                    </Col>
                </Row>
            </Container>
        </>
    )
}

export default WebCall;