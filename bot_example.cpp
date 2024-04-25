#include <vector>
#include <string>
#include <random>

using namespace std;
int TILE = 0, WIDTH = 0;

extern "C" {
    void set_first_params(int t, int w) {
      TILE = t;
      WIDTH = w;
    }
}

bool is_correct_coords(int x, int y){
    return 0 <= x <= WIDTH - TILE &&  0 < y < WIDTH;
}

extern "C" {
      char get_bot_move(int *my_pos, int my_pos_len, int **enemies_positions,
                        int enemies_positions_len, int *enemies_points,
                        int enemies_points_len, int **bombs_positions,
                        int bombs_positions_len, int **blocks_layout,
                        int blocks_layout_len, int **stones_layout,
                        int stones_layout_len) {
        vector<int> my_pos_vec(my_pos, my_pos + my_pos_len);

        vector<vector<int>> enemies_positions_vec;
        for (int i = 0; i < enemies_positions_len; ++i) {
            vector<int> temp(enemies_positions[i], enemies_positions[i] + 2);
            enemies_positions_vec.push_back(temp);
        }
        vector<int> enemies_points_vec(enemies_points, enemies_points + enemies_points_len);

        vector<vector<int>> bombs_positions_vec;
        for (int i = 0; i < bombs_positions_len; ++i) {
            vector<int> temp(bombs_positions[i], bombs_positions[i] + 2);
            bombs_positions_vec.push_back(temp);
        }
        vector<vector<int>> blocks_layout_vec;
        for (int i = 0; i < blocks_layout_len; ++i) {
            vector<int> temp(blocks_layout[i], blocks_layout[i] + 2);
            blocks_layout_vec.push_back(temp);
        }
        vector<vector<int>> stones_layout_vec;
        for (int i = 0; i < stones_layout_len; ++i) {
            vector<int> temp(stones_layout[i], stones_layout[i] + 2);
            stones_layout_vec.push_back(temp);
        }
        random_device rd;   
        mt19937 gen(rd()); 
        uniform_int_distribution<> dist(0, 4);
        vector<char> keys_to_move = {'L', 'R', 'U', 'D', 'S'};
        return keys_to_move[dist(gen)];
    }
}