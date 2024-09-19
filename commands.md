
export SHOPPING="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:7770"
export SHOPPING_ADMIN="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:7780/admin"
export REDDIT="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:9999"
export GITLAB="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:8023"
export MAP="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:3000"
export WIKIPEDIA="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:8888/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
export HOMEPAGE="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:4399" # this is a placeholder







python run.py --instruction_path agent/prompts/jsons/p_cot_id_actree_2s.json --test_start_idx 0 --test_end_idx 1 --model gpt-3.5-turbo --result_dir ./results


# Shrey = ec2-18-117-207-65.us-east-2.compute.amazonaws.com
# Mayank = ec2-13-58-203-77.us-east-2.compute.amazonaws.com



# docker start gitlab
# docker start shopping
# docker start shopping_admin
# docker start forum
# docker start kiwix33
# cd /home/ubuntu/openstreetmap-website/
# docker compose start


# docker exec shopping /var/www/magento2/bin/magento setup:store-config:set --base-url="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:7770" # no trailing /
# docker exec shopping mysql -u magentouser -pMyPassword magentodb -e  'UPDATE core_config_data SET value="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:7770/" WHERE path = "web/secure/base_url";'



# # remove the requirement to reset password
# docker exec shopping_admin php /var/www/magento2/bin/magento config:set admin/security/password_is_forced 0
# docker exec shopping_admin php /var/www/magento2/bin/magento config:set admin/security/password_lifetime 0
# docker exec shopping /var/www/magento2/bin/magento cache:flush

# docker exec shopping_admin /var/www/magento2/bin/magento setup:store-config:set --base-url="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:7780"
# docker exec shopping_admin mysql -u magentouser -pMyPassword magentodb -e  'UPDATE core_config_data SET value="http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:7780/" WHERE path = "web/secure/base_url";'
# docker exec shopping_admin /var/www/magento2/bin/magento cache:flush

# docker exec gitlab sed -i "s|^external_url.*|external_url 'http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:8023'|" /etc/gitlab/gitlab.rb
# docker exec gitlab gitlab-ctl reconfigure







# Shopping:
# http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:7770/


# Shopping Admin Panel:
# http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:7780/admin

# GitLab:
# http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:8023/users/sign_in


# Forum:
# http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:9999/

# OpenStreetMap:
# http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:3000/


# Wikipedia:
# http://ec2-13-58-203-77.us-east-2.compute.amazonaws.com:8888/