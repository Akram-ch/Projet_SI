#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

in vec3 position;
in vec3 tex_coord;
in vec3 normal;

out vec2 frag_tex_coords;
// position and normal for the fragment shader, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
out vec3 w_position, w_normal;   // in world coordinates
out float visibility;


const float density = 0.03;
const float gradient = 1.5;

void main() {
    // TODO: compute the vertex position and normal in world or view coordinates
    // model doit être une transformation isométrique pour ne pas changer l'orientation de la normale de la surface
    // sinon on perd l'orthogonalité de la normale par rapport à sa face. (elle peut aussi être seulement orthogonale)
    // Une solution est de multiplier après-coup la normale par (M^-1)^T où M représente la matrice model.
    vec4 positionRelativeToCam = view * vec4(position, 1);
    w_normal = (transpose(inverse(model)) * vec4(normal, 0)).xyz;

    w_position = (model * vec4(position, 1)).xyz;

    // tell OpenGL how to transform the vertex to clip coordinates
    gl_Position = projection * view * model * vec4(position, 1);
    
    float distance = length(positionRelativeToCam.xyz);
    visibility = exp(-pow((distance*density), gradient));
    // fragment texture plane coordinates
    frag_tex_coords = tex_coord.xy;
}
