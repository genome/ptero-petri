local dest_hash_key = KEYS[1]

local expire_key = function(key)
    redis.call('EXPIRE', key, 90 * 24 * 3600)
end

for i = 2, #KEYS do
    local src_hash_key = KEYS[i]

    for j, hkey in pairs(redis.call("HKEYS", src_hash_key)) do
        local src_value = redis.call("HGET", src_hash_key, hkey)
        local rv = redis.call("HSETNX", dest_hash_key, hkey, src_value)
        expire_key(dest_hash_key)

        if rv == 0 then
            if not (src_value == redis.call("HGET", dest_hash_key, hkey)) then
                return {-1, string.format("Conflicting data in key (%s)", hkey)}
            end
        end
    end
end

return {0, "Success"}
