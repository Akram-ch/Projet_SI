#version 330 core

// fragment position and normal of the fragment, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
in vec3 w_position, w_normal;   // in world coodinates

// Sampler2D is a GLSL unique type associated to a complete texture format
uniform sampler2D diffuse_map;

// light dir, in world coordinates
uniform vec3 light_dir;

// material properties
uniform vec3 k_d;
uniform vec3 k_s;
uniform vec3 k_a;
uniform float s;

// world camera position
uniform vec3 w_camera_position;

// fragment texture plane coordinates
in vec2 frag_tex_coords;

// output fragment color for OpenGL
out vec4 out_color;

void main() {
    // TODO: compute Lambert illumination
    // I = max (k_d (light_dir . w_normal) , 0 )
    // normalize(I)

    // dot product
    float scal = dot(light_dir, w_normal);

    // max
    scal = max(scal, 0);

    // Compute all vectors, oriented outwards from the fragment
    // vec3 n = normalize(w_normal);
    // vec3 l = normalize(-light_dir);
    // vec3 r = reflect(-l, n);
    // vec3 v = normalize(w_camera_position - w_position);

    // vec3 diffuse_color = k_d * max(dot(n, l), 0);
    // vec3 specular_color = k_s * pow(max(dot(r, v), 0), s);    

    out_color = scal * vec4(texture(diffuse_map, frag_tex_coords).rgb, 1);

    // normalize
    // out_color = normalize(out_color);

    // We need two other terms to make phong approx :
    // K_a
    // K_s (r . v)^s = pow(dot(reflect (w_normal, -light_dir), w_camera_position), s) * K_s

    
    out_color += pow(dot(reflect (w_normal, -light_dir), w_camera_position), s) * vec4(k_s,1) + vec4(k_a,1);

}
