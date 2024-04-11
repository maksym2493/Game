//table-row

class ProfileTable{
    constructor(){
        this.my_profile = true;

        this.profile = document.querySelector('.profile');
        this.error_table = this.profile.querySelector('#error_table');
        this.profile_table = this.profile.querySelector('#profile_table')

        this.id = this.profile_table.querySelector('#id');
        this.login = this.profile_table.querySelector('#login');

        this.exp = this.profile_table.querySelector('#exp');
        this.level = this.profile_table.querySelector('#level');

        this.last_online_tr = this.profile_table.querySelector('#last_online_tr');
        this.last_online = this.last_online_tr.querySelector('#last_online');

        this.top_tr = this.profile_table.querySelector('#top_tr');

        this.global_top_tr = this.profile_table.querySelector('#global_top_tr');
        this.global_pos = this.global_top_tr.querySelector('#global_pos');
        this.global_score = this.global_top_tr.querySelector('#global_score');

        this.season_top_tr = this.profile_table.querySelector('#season_top_tr');
        this.season_pos = this.season_top_tr.querySelector('#season_pos');
        this.season_score = this.season_top_tr.querySelector('#season_score');
    }
    
    async back(){
        if(!this.my_profile){
            this.my_profile = true;

            this.close();
            await top_table.open();
            
            return;
        }

        this.close();
        menu_table.open();
    }

    async open(user_id = null){
        let user = client.user;
        
        toggle(this.profile, 'table');

        if(user_id != null){
            this.my_profile = false;
            user = await client.get_profile(user_id);
            
            if(user.error != null){
                if(user.error == 'Користувач не знайдений.'){
                    this.error_table.style.display = 'table-row';
                    return;
                }
                
                if(user.need_login){
                    this.close();
                    game_table.close();
                    login_table.open();
                }

                return;
            }

            if(user.last_online != null){
                this.last_online_tr.style.display = 'table-row';
                this.last_online.innerHTML = get_time_delta(user.last_online);
            }
        }
        else{
            user = await client.get_profile();
            
            if(user.error != null){
                if(user.error == 'Користувач не знайдений.'){
                    this.error_table.style.display = 'table-row';
                    return;
                }

                if(user.need_login){
                    this.close();
                    game_table.close();
                    login_table.open();
                }
                
                return;
            }
        }

        this.profile_table.style.display = 'table-row';

        this.id.innerHTML = transform_digit(user.user_id);
        this.login.innerHTML = user.login;

        this.exp.innerHTML = this.get_exp(user);
        this.level.innerHTML = this.get_level(user);

        if(user.global_pos != null){
            if(this.top_tr.style.display == 'none'){ this.top_tr.style.display = 'table-row'; }
            
            this.global_top_tr.style.display = 'table-row';
            this.global_pos.innerHTML = transform_digit(user.global_pos);
            this.global_score.innerHTML = transform_digit(user.global_score);
        }

        if(user.season_pos != null){
            if(this.top_tr.style.display == 'none'){ this.top_tr.style.display = 'table-row'; }
            
            this.season_top_tr.style.display = 'table-row';
            this.season_pos.innerHTML = transform_digit(user.season_pos);
            this.season_score.innerHTML = transform_digit(user.season_score);
        }
    }

    new_top_pos(){ if(this.profile_table.style.display == 'table-row' && this.my_profile){ this.season_pos.innerHTML = client.user.season_pos; } }
    update(){ if(this.profile_table.style.display == 'table-row'){ this.open(); } }
    
    close(){
        toggle(this.profile);
        if(this.error_table.style.display == 'table-row'){ this.error_table.style.display = 'none'; return; }

        this.profile_table.style.display = 'none';

        this.id.innerHTML = '';
        this.login.innerHTML = '';

        this.exp.innerHTML = '';
        this.level.innerHTML = '';

        if(this.last_online_tr.style.display == 'table-row'){
            this.last_online_tr.style.display = 'none';
            this.last_online.innerHTML = '';
        }

        if(this.top_tr.style.display == 'table-row'){
            this.top_tr.style.display = 'none';
            
            if(this.global_top_tr.style.display  == 'table-row'){
                this.global_top_tr.style.display = 'none';

                this.global_pos.innerHTML = '';
                this.global_score.innerHTML = '';
            }
            
            if(this.season_top_tr.style.display  == 'table-row'){
                this.season_top_tr.style.display = 'none';

                this.season_pos.innerHTML = '';
                this.season_score.innerHTML = '';
            }
        }
    }

    get_level(user){
        const level = user.level;
        return `${transform_digit(level.level)}-ий - ${((level.exp[0] / level.exp[1]) * 100).toFixed(4)}%`;
    }
    
    get_exp(user){
        const level = user.level;
        return `[ ${transform_digit(level.exp[0])} з ${transform_digit(level.exp[1])} ]`;
    }
}