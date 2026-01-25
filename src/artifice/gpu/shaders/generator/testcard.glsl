#version 430

layout(local_size_x = 16, local_size_y = 16) in;

layout(rgba32f, binding = 0) writeonly uniform image2D output_image;

uniform int size;
uniform int seed;
uniform float time;  // For animated effects if desired

// Hash function for noise
uint hash(uint x) {
    x += (x << 10u);
    x ^= (x >> 6u);
    x += (x << 3u);
    x ^= (x >> 11u);
    x += (x << 15u);
    return x;
}

uint hash2(uvec2 v) {
    return hash(v.x ^ hash(v.y));
}

float random(uvec2 pos, uint s) {
    return float(hash2(pos + uvec2(s, s * 17u))) / 4294967295.0;
}

// Smoothstep for noise interpolation
float smootherstep(float t) {
    return t * t * (3.0 - 2.0 * t);
}

// Simple value noise
float valueNoise(vec2 p, float scale, uint s) {
    vec2 scaled = p / scale;
    vec2 i = floor(scaled);
    vec2 f = fract(scaled);

    // Smooth interpolation
    f.x = smootherstep(f.x);
    f.y = smootherstep(f.y);

    // Four corners
    float a = random(uvec2(i), s);
    float b = random(uvec2(i) + uvec2(1, 0), s);
    float c = random(uvec2(i) + uvec2(0, 1), s);
    float d = random(uvec2(i) + uvec2(1, 1), s);

    // Bilinear interpolation
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// HSV to RGB conversion
vec3 hsv2rgb(vec3 hsv) {
    float h = hsv.x * 6.0;
    float s = hsv.y;
    float v = hsv.z;

    float c = v * s;
    float x = c * (1.0 - abs(mod(h, 2.0) - 1.0));
    float m = v - c;

    vec3 rgb;
    if (h < 1.0) rgb = vec3(c, x, 0.0);
    else if (h < 2.0) rgb = vec3(x, c, 0.0);
    else if (h < 3.0) rgb = vec3(0.0, c, x);
    else if (h < 4.0) rgb = vec3(0.0, x, c);
    else if (h < 5.0) rgb = vec3(x, 0.0, c);
    else rgb = vec3(c, 0.0, x);

    return rgb + m;
}

void main() {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);

    if (pos.x >= size || pos.y >= size) {
        return;
    }

    // Normalized coordinates
    vec2 uv = vec2(pos) / float(size);

    // Cell dimensions (4x4 grid for top, 2 full-width rows at bottom)
    int cell_size = size / 4;
    int cell_x = pos.x / cell_size;
    int cell_y = pos.y / cell_size;

    // Local position within cell
    vec2 local = vec2(pos.x % cell_size, pos.y % cell_size) / float(cell_size);

    vec3 color = vec3(0.0);

    // Row 0: Color bars, Checkerboard 8x8, Diagonal lines, Zone plate
    if (cell_y == 0) {
        if (cell_x == 0) {
            // Color bars (RGBCMYWK)
            int bar = int(local.x * 8.0);
            if (bar == 0) color = vec3(1.0, 0.0, 0.0);       // Red
            else if (bar == 1) color = vec3(0.0, 1.0, 0.0);  // Green
            else if (bar == 2) color = vec3(0.0, 0.0, 1.0);  // Blue
            else if (bar == 3) color = vec3(0.0, 1.0, 1.0);  // Cyan
            else if (bar == 4) color = vec3(1.0, 0.0, 1.0);  // Magenta
            else if (bar == 5) color = vec3(1.0, 1.0, 0.0);  // Yellow
            else if (bar == 6) color = vec3(1.0, 1.0, 1.0);  // White
            else color = vec3(0.0, 0.0, 0.0);                // Black
        }
        else if (cell_x == 1) {
            // Checkerboard 8x8
            int cx = int(local.x * 8.0);
            int cy = int(local.y * 8.0);
            color = vec3(float((cx + cy) % 2));
        }
        else if (cell_x == 2) {
            // Diagonal lines
            int stripe = int((local.x + local.y) * 8.0);
            color = vec3(float(stripe % 2));
        }
        else {
            // Zone plate (Fresnel pattern)
            vec2 center = vec2(0.5);
            float r2 = dot(local - center, local - center) * 4.0;
            float zone = sin(25.0 * r2 * 3.14159) * 0.5 + 0.5;
            color = vec3(zone);
        }
    }
    // Row 1: Step wedge, Radial gradient, Fine checkerboard, Perlin noise
    else if (cell_y == 1) {
        if (cell_x == 0) {
            // Step wedge (8 discrete levels)
            int step_idx = int(local.x * 8.0);
            color = vec3(float(step_idx) / 7.0);
        }
        else if (cell_x == 1) {
            // Radial gradient
            vec2 center = vec2(0.5);
            float dist = length(local - center) * 2.0;
            float radial = 1.0 - clamp(dist / 1.414, 0.0, 1.0);
            color = vec3(radial);
        }
        else if (cell_x == 2) {
            // Fine checkerboard 16x16
            int cx = int(local.x * 16.0);
            int cy = int(local.y * 16.0);
            color = vec3(float((cx + cy) % 2));
        }
        else {
            // Perlin-like noise
            float noise = valueNoise(vec2(pos), float(cell_size) / 8.0, uint(seed));
            color = vec3(noise);
        }
    }
    // Row 2: Rainbow hue sweep (full width)
    else if (cell_y == 2) {
        color = hsv2rgb(vec3(uv.x, 1.0, 1.0));
    }
    // Row 3: Grayscale gradient (full width)
    else {
        color = vec3(uv.x);
    }

    imageStore(output_image, pos, vec4(color, 1.0));
}
