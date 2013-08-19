var app = angular.module('article', []);

app.config(function($routeProvider, $locationProvider) {
    $routeProvider
        .when('/:category/:name', {
            templateUrl: function(params) {
                return 'articles/' + params.category + '/' + params.name + '.html';
            },
            controller: 'ArticleCtrl'
        })
        .otherwise({
            redirectTo: '/'
        });
    $locationProvider
        .html5Mode(false)
        .hashPrefix('!');
});


app.controller('ArticleCtrl', function($scope, $route, $routeParams) {
    
})

app.controller('NavbarCtrl', function($scope, $location) {
    console.log($location);
    console.log($location.path());
    $scope.path = $location.path;
})