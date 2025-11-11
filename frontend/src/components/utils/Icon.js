import React from "react";

function Icon({ svg, size = 24, color = "currentColor" }) {
    return (
        <span
            style={{
                display: "inline-flex",
                verticalAlign: "middle",
                width: size,
                height: size,
                color,
            }}
            dangerouslySetInnerHTML={{ __html: svg }}
        />
    );
}

export default Icon;
