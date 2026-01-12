import React, { useEffect, useState } from 'react'
import './Style.css'
import image1 from "../assets/BackgroundImages/Image1.jpg"
import image2 from "../assets/BackgroundImages/Image2.jpg"
import image3 from "../assets/BackgroundImages/Image3.jpg"
import image4 from "../assets/BackgroundImages/Image4.png"

const images = [image1, image2, image3, image4];

function Background() {
    const [slide, setSlide] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setSlide((prev => (prev +1) % images.length));
        }, 10000);

        return () => clearInterval(interval);
    }, []);


    return (
        <div className="background-container">
            <div className="imagesBG">
                {images.map((img, index) => (
                    <img
                        key={index}
                        src={img}
                        alt='Background'
                        className={index === slide ? 'active' : ""}
                    />
                ))}
            </div>
            <div className="overlay"></div>
            <div className="text-bg"><p>Rent a car!</p><p>Rent your dream!</p></div>
        </div>
    )
}

export default Background