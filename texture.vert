#version 330 core

// input attribute variable, given per vertex
in vec3 position;
in vec3 normal;

in vec3 tex_coord;

uniform mat4 model, view, projection;

out vec2 frag_tex_coords;
// position and normal for the fragment shader, in WORLD coordinates
out vec3 w_position, w_normal;   // in world coordinates
out float visibility;

const float density = 0.04;
const float gradient = 1.5;

void main() {
    vec4 w_position4 = model * vec4(position, 1.0);
    vec4 positionRelativeToCam = view * vec4(w_position, 1.0);
    gl_Position = projection * view * w_position4;

    // fragment position in world coordinates
    w_position = w_position4.xyz / w_position4.w;  // dehomogenize

    // fragment normal in world coordinates
    mat3 nit_matrix = transpose(inverse(mat3(model)));
    w_normal = normalize(nit_matrix * normal);
    frag_tex_coords = tex_coord.xy;

    float distance = length(positionRelativeToCam.xyz);
    visibility = exp(-pow((distance*density), gradient));
}